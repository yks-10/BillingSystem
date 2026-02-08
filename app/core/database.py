import logging
from typing import Optional, Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, event, pool
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()


class DatabaseConnection:
    """
    Singleton class for PostgreSQL database connectivity.
    Manages database engine, sessions, and connection pooling.
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    
    def __new__(cls) -> 'DatabaseConnection':
        """
        Implement singleton pattern - ensure only one instance exists.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialize database connection (only once due to singleton pattern).
        """
        # Prevent re-initialization
        if self._engine is not None:
            return
        
        self._initialize_engine()
        self._initialize_session_factory()
        self._setup_event_listeners()
        logger.info("Database connection initialized successfully")
    
    def _initialize_engine(self) -> None:
        """
        Create and configure the SQLAlchemy engine with connection pooling.
        """
        try:
            self._engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_pre_ping=True,  # Verify connections before using them
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=settings.DB_ECHO,
                future=True,
                connect_args={
                    "connect_timeout": 10,
                    "application_name": settings.APP_NAME,
                }
            )
            logger.info(f"Database engine created: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
        except Exception as e:
            logger.error(f"Failed to create database engine: {str(e)}")
            raise
    
    def _initialize_session_factory(self) -> None:
        """
        Create session factory for database sessions.
        """
        if self._engine is None:
            raise RuntimeError("Database engine not initialized")
        
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        logger.info("Session factory initialized")
    
    def _setup_event_listeners(self) -> None:
        """
        Setup SQLAlchemy event listeners for connection management.
        """
        if self._engine is None:
            return
        
        @event.listens_for(self._engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Event listener for new connections."""
            logger.debug("New database connection established")
        
        @event.listens_for(self._engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Event listener for connection checkout from pool."""
            logger.debug("Connection checked out from pool")
    
    @property
    def engine(self) -> Engine:
        """
        Get the database engine instance.
        
        Returns:
            SQLAlchemy Engine instance
        """
        if self._engine is None:
            raise RuntimeError("Database engine not initialized")
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """
        Get the session factory.
        
        Returns:
            SQLAlchemy sessionmaker instance
        """
        if self._session_factory is None:
            raise RuntimeError("Session factory not initialized")
        return self._session_factory
    
    def get_session(self) -> Session:
        """
        Create and return a new database session.
        
        Returns:
            SQLAlchemy Session instance
        """
        if self._session_factory is None:
            raise RuntimeError("Session factory not initialized")
        return self._session_factory()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.
        
        Usage:
            with db.session_scope() as session:
                # Perform database operations
                session.add(obj)
        
        Yields:
            SQLAlchemy Session instance
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
            logger.debug("Database transaction committed")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database transaction rolled back: {str(e)}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error, transaction rolled back: {str(e)}")
            raise
        finally:
            session.close()
            logger.debug("Database session closed")
    
    def create_tables(self) -> None:
        """
        Create all database tables based on SQLAlchemy models.
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            raise
    
    def drop_tables(self) -> None:
        """
        Drop all database tables. Use with caution!
        """
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test database connectivity.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def close(self) -> None:
        """
        Close all database connections and dispose of the engine.
        """
        if self._engine is not None:
            self._engine.dispose()
            logger.info("Database connections closed and engine disposed")
    
    def get_pool_status(self) -> dict:
        """
        Get current connection pool status.
        
        Returns:
            dict: Pool statistics including size, checked in/out connections
        """
        if self._engine is None:
            return {}
        
        pool = self._engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total": pool.size() + pool.overflow()
        }


# Global database instance
db = DatabaseConnection()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database sessions.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            # Use db session here
            pass
    
    Yields:
        SQLAlchemy Session instance
    """
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """
    Initialize database - create tables if they don't exist.
    """
    logger.info("Initializing database...")
    db.create_tables()
    logger.info("Database initialization complete")


def close_db() -> None:
    """
    Close database connections - call on application shutdown.
    """
    logger.info("Closing database connections...")
    db.close()
    logger.info("Database connections closed")
