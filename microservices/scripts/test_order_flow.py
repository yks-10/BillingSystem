"""Test complete order flow through microservices."""

import httpx
import asyncio
import json

API_GATEWAY = "http://localhost:8000/api"


async def test_order_flow():
    """Test complete order creation flow."""
    print("\n" + "=" * 60)
    print("🧪 Testing Order Flow")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Check available products
        print("\n📦 Step 1: Fetching products...")
        response = await client.get(f"{API_GATEWAY}/products")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Found {len(products)} products")
            if products:
                print(f"   Example: {products[0]['product_id']} - {products[0]['name']} (₹{products[0]['price']})")
        else:
            print(f"❌ Failed to fetch products: {response.status_code}")
            return
        
        # 2. Check denominations
        print("\n💵 Step 2: Checking denominations...")
        response = await client.get(f"{API_GATEWAY}/denominations")
        if response.status_code == 200:
            denoms = response.json()
            print(f"✅ Found {len(denoms)} denominations")
        else:
            print(f"❌ Failed to fetch denominations: {response.status_code}")
            return
        
        # 3. Create a test order
        print("\n🛒 Step 3: Creating test order...")
        order_data = {
            "customer_email": "test@example.com",
            "items": [
                {"product_id": "P001", "quantity": 1},
                {"product_id": "P002", "quantity": 2}
            ],
            "paid_amount": 60000.0
        }
        
        print(f"   Order details: {json.dumps(order_data, indent=2)}")
        
        response = await client.post(
            f"{API_GATEWAY}/billing",
            json=order_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("\n✅ Order created successfully!")
            print(f"   Order ID: {result['order_id']}")
            print(f"   Customer: {result['customer_email']}")
            print(f"   Total: ₹{result['total_amount']:.2f}")
            print(f"   Paid: ₹{result['paid_amount']:.2f}")
            print(f"   Balance: ₹{result['balance_amount']:.2f}")
            
            if result['balance_denominations']:
                print("\n   Change denominations:")
                for denom, count in sorted(result['balance_denominations'].items(), reverse=True):
                    print(f"      ₹{denom} x {count} = ₹{int(denom) * count}")
            
            order_id = result['order_id']
            
            # 4. Fetch order details
            print(f"\n📋 Step 4: Fetching order details...")
            response = await client.get(f"{API_GATEWAY}/orders/{order_id}")
            if response.status_code == 200:
                order = response.json()
                print(f"✅ Order #{order_id} retrieved successfully")
                if order.get('items'):
                    print(f"   Contains {len(order['items'])} item(s)")
            
            # 5. Check customer order history
            print(f"\n📜 Step 5: Checking customer order history...")
            response = await client.get(
                f"{API_GATEWAY}/orders/customer/test@example.com"
            )
            if response.status_code == 200:
                orders = response.json()
                print(f"✅ Customer has {len(orders)} order(s)")
            
        else:
            print(f"\n❌ Failed to create order: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    
    print("\n" + "=" * 60)
    print("✅ Order flow test completed successfully!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   - Check email inbox for invoice (if configured)")
    print("   - Verify product stock was reduced")
    print("   - View order in database")


async def main():
    """Main test function."""
    try:
        await test_order_flow()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")


if __name__ == "__main__":
    asyncio.run(main())
