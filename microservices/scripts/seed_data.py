"""Seed data for microservices."""

import httpx
import asyncio
from typing import List, Dict

# Service URLs
PRODUCT_SERVICE = "http://localhost:8001"
DENOMINATION_SERVICE = "http://localhost:8003"

# Sample products
PRODUCTS = [
    {"product_id": "P001", "name": "Laptop", "price": 50000.0, "tax_percentage": 18.0, "available_stock": 10},
    {"product_id": "P002", "name": "Mouse", "price": 500.0, "tax_percentage": 18.0, "available_stock": 50},
    {"product_id": "P003", "name": "Keyboard", "price": 1500.0, "tax_percentage": 18.0, "available_stock": 30},
    {"product_id": "P004", "name": "Monitor", "price": 15000.0, "tax_percentage": 18.0, "available_stock": 15},
    {"product_id": "P005", "name": "Headphones", "price": 2000.0, "tax_percentage": 18.0, "available_stock": 25},
    {"product_id": "P006", "name": "Webcam", "price": 3000.0, "tax_percentage": 18.0, "available_stock": 20},
    {"product_id": "P007", "name": "USB Cable", "price": 200.0, "tax_percentage": 18.0, "available_stock": 100},
    {"product_id": "P008", "name": "External HDD", "price": 5000.0, "tax_percentage": 18.0, "available_stock": 15},
    {"product_id": "P009", "name": "Printer", "price": 8000.0, "tax_percentage": 18.0, "available_stock": 8},
    {"product_id": "P010", "name": "Scanner", "price": 6000.0, "tax_percentage": 18.0, "available_stock": 12},
]

# Denominations (Indian currency)
DENOMINATIONS = [
    {"value": 2000, "available_count": 50},
    {"value": 500, "available_count": 100},
    {"value": 200, "available_count": 100},
    {"value": 100, "available_count": 200},
    {"value": 50, "available_count": 100},
    {"value": 20, "available_count": 150},
    {"value": 10, "available_count": 200},
    {"value": 5, "available_count": 100},
    {"value": 2, "available_count": 100},
    {"value": 1, "available_count": 100},
]


async def seed_products():
    """Seed products into Product Service."""
    print("\n🌱 Seeding products...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        for product in PRODUCTS:
            try:
                response = await client.post(
                    f"{PRODUCT_SERVICE}/products",
                    json=product
                )
                if response.status_code in [200, 201]:
                    print(f"✅ Created product: {product['product_id']} - {product['name']}")
                else:
                    print(f"⚠️  Product {product['product_id']} might already exist or error occurred")
            except Exception as e:
                print(f"❌ Error creating product {product['product_id']}: {e}")


async def seed_denominations():
    """Seed denominations into Denomination Service."""
    print("\n💵 Seeding denominations...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        for denom in DENOMINATIONS:
            try:
                response = await client.post(
                    f"{DENOMINATION_SERVICE}/denominations",
                    json=denom
                )
                if response.status_code in [200, 201]:
                    print(f"✅ Created denomination: ₹{denom['value']} x {denom['available_count']}")
                else:
                    print(f"⚠️  Denomination ₹{denom['value']} might already exist or error occurred")
            except Exception as e:
                print(f"❌ Error creating denomination ₹{denom['value']}: {e}")


async def check_services():
    """Check if services are running."""
    print("\n🔍 Checking services...")
    services = [
        ("Product Service", PRODUCT_SERVICE),
        ("Denomination Service", DENOMINATION_SERVICE),
    ]
    
    all_healthy = True
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services:
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    print(f"✅ {name} is healthy")
                else:
                    print(f"❌ {name} returned status {response.status_code}")
                    all_healthy = False
            except Exception as e:
                print(f"❌ {name} is not reachable: {e}")
                all_healthy = False
    
    return all_healthy


async def main():
    """Main seeding function."""
    print("=" * 60)
    print("🌱 Microservices Data Seeder")
    print("=" * 60)
    
    # Check services
    if not await check_services():
        print("\n⚠️  Some services are not healthy. Please ensure all services are running:")
        print("   docker-compose up -d")
        return
    
    # Seed data
    await seed_products()
    await seed_denominations()
    
    print("\n" + "=" * 60)
    print("✅ Seeding completed!")
    print("=" * 60)
    print("\n💡 You can now:")
    print("   - View API docs: http://localhost:8000/docs")
    print("   - Create an order via API Gateway")
    print("   - Check service health: curl http://localhost:8000/health")


if __name__ == "__main__":
    asyncio.run(main())
