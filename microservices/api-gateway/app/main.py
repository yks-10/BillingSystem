"""API Gateway FastAPI application."""

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import sys
from pathlib import Path
from typing import Dict, Any
import logging

# Add parent directory to path for shared modules
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="Central gateway for all microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service registry
SERVICE_ROUTES = {
    "/api/products": settings.PRODUCT_SERVICE_URL,
    "/api/billing": settings.ORDER_SERVICE_URL,
    "/api/orders": settings.ORDER_SERVICE_URL,
    "/api/denominations": settings.DENOMINATION_SERVICE_URL,
    "/api/notifications": settings.NOTIFICATION_SERVICE_URL,
}


async def forward_request(
    request: Request,
    target_url: str,
    path: str
) -> Response:
    """
    Forward request to target service.
    
    Args:
        request: Incoming FastAPI request
        target_url: Base URL of target service
        path: Path to forward
        
    Returns:
        Response from target service
    """
    # Build full URL
    url = f"{target_url.rstrip('/')}{path}"
    
    # Get request body
    body = await request.body()
    
    # Prepare headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    logger.info(f"Forwarding {request.method} {url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
    except httpx.RequestError as e:
        logger.error(f"Error forwarding request to {url}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/")
async def root():
    """API Gateway root endpoint."""
    return {
        "service": "API Gateway",
        "version": "1.0.0",
        "status": "running",
        "available_services": list(SERVICE_ROUTES.keys())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check health of all services
    health_status = {"gateway": "healthy", "services": {}}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for route, service_url in SERVICE_ROUTES.items():
            service_name = route.split("/")[-1]
            try:
                response = await client.get(f"{service_url}/health")
                if response.status_code == 200:
                    health_status["services"][service_name] = "healthy"
                else:
                    health_status["services"][service_name] = "unhealthy"
            except Exception as e:
                health_status["services"][service_name] = f"unreachable: {str(e)}"
    
    # Overall status
    all_healthy = all(
        status == "healthy" 
        for status in health_status["services"].values()
    )
    health_status["overall"] = "healthy" if all_healthy else "degraded"
    
    return health_status


# Dynamic routing for all API requests
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def api_router(request: Request, path: str):
    """
    Route API requests to appropriate microservices.
    
    Routing logic:
    - /api/products/* -> Product Service
    - /api/billing/* -> Order Service
    - /api/orders/* -> Order Service
    - /api/denominations/* -> Denomination Service
    - /api/notifications/* -> Notification Service
    """
    # Determine target service
    target_service = None
    service_path = f"/{path}"
    
    for route_prefix, service_url in SERVICE_ROUTES.items():
        # Extract the service part (e.g., "products" from "/api/products")
        service_part = route_prefix.replace("/api/", "")
        
        if path.startswith(service_part):
            target_service = service_url
            # Remove service prefix from path for forwarding
            service_path = "/" + path.replace(service_part, "", 1).lstrip("/")
            if not service_path or service_path == "/":
                service_path = f"/{service_part}"
            else:
                service_path = f"/{service_part}{service_path}"
            break
    
    if not target_service:
        raise HTTPException(
            status_code=404,
            detail=f"No service found for path: /api/{path}"
        )
    
    # Forward request
    return await forward_request(request, target_service, service_path)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found",
            "path": str(request.url),
            "available_routes": list(SERVICE_ROUTES.keys())
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors."""
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
