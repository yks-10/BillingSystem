"""
Data seeding script for the billing system.
This script populates the database with initial products and denominations.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db, Base
from app.models.product import Product
from app.models.denomination import Denomination


def seed_products():
    """Seed initial products into the database."""
    session = db.get_session()
    
    try:
        # Check if products already exist
        existing_products = session.query(Product).count()
        if existing_products > 0:
            print(f"Products already exist ({existing_products} found). Skipping product seeding.")
            return
        
        products = [
            Product(
                product_id="P001",
                name="Laptop",
                price=50000.00,
                tax_percentage=18.0,
                available_stock=10
            ),
            Product(
                product_id="P002",
                name="Mouse",
                price=500.00,
                tax_percentage=12.0,
                available_stock=50
            ),
            Product(
                product_id="P003",
                name="Keyboard",
                price=1500.00,
                tax_percentage=12.0,
                available_stock=30
            ),
            Product(
                product_id="P004",
                name="Monitor",
                price=15000.00,
                tax_percentage=18.0,
                available_stock=15
            ),
            Product(
                product_id="P005",
                name="Headphones",
                price=2000.00,
                tax_percentage=12.0,
                available_stock=40
            ),
            Product(
                product_id="P006",
                name="USB Cable",
                price=200.00,
                tax_percentage=12.0,
                available_stock=100
            ),
            Product(
                product_id="P007",
                name="Webcam",
                price=3000.00,
                tax_percentage=18.0,
                available_stock=25
            ),
            Product(
                product_id="P008",
                name="External Hard Drive",
                price=4500.00,
                tax_percentage=18.0,
                available_stock=20
            ),
            Product(
                product_id="P009",
                name="Phone Charger",
                price=800.00,
                tax_percentage=12.0,
                available_stock=60
            ),
            Product(
                product_id="P010",
                name="Power Bank",
                price=1200.00,
                tax_percentage=12.0,
                available_stock=35
            ),
        ]
        
        db.add_all(products)
        db.commit()
        print(f"Successfully seeded {len(products)} products!")
        
        # Display seeded products
        print("\nSeeded Products:")
        print("-" * 80)
        for product in products:
            print(f"  {product.product_id}: {product.name} - ₹{product.price} (Tax: {product.tax_percentage}%) - Stock: {product.available_stock}")
        
    except Exception as e:
        print(f"Error seeding products: {str(e)}")
        session.rollback()
    finally:
        session.close()


def seed_denominations():
    """Seed denomination values into the database."""
    session = db.get_session()
    
    try:
        # Check if denominations already exist
        existing_denoms = session.query(Denomination).count()
        if existing_denoms > 0:
            print(f"\nDenominations already exist ({existing_denoms} found). Skipping denomination seeding.")
            return
        
        # Indian currency denominations
        denominations = [
            Denomination(value=2000, available_count=10),
            Denomination(value=500, available_count=20),
            Denomination(value=200, available_count=20),
            Denomination(value=100, available_count=30),
            Denomination(value=50, available_count=40),
            Denomination(value=20, available_count=50),
            Denomination(value=10, available_count=100),
            Denomination(value=5, available_count=100),
            Denomination(value=2, available_count=50),
            Denomination(value=1, available_count=100),
        ]
        
        db.add_all(denominations)
        db.commit()
        print(f"\nSuccessfully seeded {len(denominations)} denominations!")
        
        # Display seeded denominations
        print("\nSeeded Denominations:")
        print("-" * 50)
        for denom in denominations:
            print(f"  ₹{denom.value}: {denom.available_count} notes/coins")
        
    except Exception as e:
        print(f"Error seeding denominations: {str(e)}")
        session.rollback()
    finally:
        session.close()


def main():
    """Main function to seed all data."""
    print("=" * 80)
    print("BILLING SYSTEM - DATABASE SEEDING")
    print("=" * 80)
    
    # Create tables if they don't exist
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=db.engine)
    print("Database tables ready!")
    
    # Seed data
    print("\n" + "=" * 80)
    print("SEEDING DATA")
    print("=" * 80)
    
    seed_products()
    seed_denominations()
    
    print("\n" + "=" * 80)
    print("SEEDING COMPLETED!")
    print("=" * 80)
    print("\nYou can now start using the billing system.")
    print("Run the application with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
