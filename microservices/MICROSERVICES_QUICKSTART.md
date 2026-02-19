# Microservices Quick Start Guide

## 🚀 Get Started in 5 Minutes

Your billing system has been converted to a microservices architecture! Here's how to run it:

### 1. Navigate to Microservices Directory

```bash
cd microservices
```

### 2. Start All Services

```bash
# Using Docker Compose (Recommended)
docker-compose up -d --build

# Or using Make
make start-all
```

### 3. Verify Services

```bash
# Check health
curl http://localhost:8000/health

# Or
make health
```

### 4. Seed Initial Data

```bash
cd scripts
pip3 install -r requirements.txt
python3 seed_data.py
```

### 5. Test the System

```bash
# View API documentation
open http://localhost:8000/docs

# Run automated test
python3 test_order_flow.py
```

## 🎯 What You Get

### 5 Independent Microservices

1. **API Gateway** (http://localhost:8000)
   - Single entry point for all requests
   - Routes to appropriate services
   
2. **Product Service** (http://localhost:8001)
   - Product CRUD operations
   - Stock management
   
3. **Order Service** (http://localhost:8002)
   - Order processing
   - Billing calculations
   
4. **Denomination Service** (http://localhost:8003)
   - Cash denomination management
   - Change calculation
   
5. **Notification Service** (http://localhost:8004)
   - Email notifications
   - Invoice generation

### 3 PostgreSQL Databases

- `product_db` (port 5433)
- `order_db` (port 5434)
- `denomination_db` (port 5435)

## 📚 Key Endpoints

All requests go through the API Gateway (http://localhost:8000/api):

### Products
```bash
# List products
GET /api/products

# Create product
POST /api/products

# Get product
GET /api/products/{id}
```

### Orders
```bash
# Create order/bill
POST /api/billing

# Get orders
GET /api/orders

# Get customer orders
GET /api/orders/customer/{email}
```

### Denominations
```bash
# List denominations
GET /api/denominations

# Calculate change
POST /api/denominations/calculate-change
```

## 🛠️ Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean and restart
make clean && make start-all

# Check running services
docker-compose ps

# Run tests
make test
```

## 📖 Documentation

- **Detailed Guide**: [IMPLEMENTATION_GUIDE.md](microservices/IMPLEMENTATION_GUIDE.md)
- **Architecture Details**: [MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md)
- **Full README**: [microservices/README.md](microservices/README.md)

## 🎉 Example Usage

### Create a Product

```bash
curl -X POST "http://localhost:8000/api/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "P999",
    "name": "Test Product",
    "price": 100.0,
    "tax_percentage": 18.0,
    "available_stock": 50
  }'
```

### Create an Order

```bash
curl -X POST "http://localhost:8000/api/billing" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "customer@example.com",
    "items": [
      {"product_id": "P001", "quantity": 1}
    ],
    "paid_amount": 60000.0
  }'
```

## 🔍 Monitoring

- **API Gateway Health**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Individual Services**: http://localhost:800[1-4]/docs

## 💡 Tips

1. Use the Swagger UI for interactive testing
2. Check logs when debugging: `docker-compose logs [service-name]`
3. Use Make commands for convenience: `make help`
4. All services auto-restart on failure
5. Databases have persistent volumes

## 🐛 Issues?

```bash
# Restart everything
docker-compose restart

# View logs
docker-compose logs -f

# Clean slate
make clean && make start-all
```

## 📞 Help

- Check [IMPLEMENTATION_GUIDE.md](microservices/IMPLEMENTATION_GUIDE.md) for detailed steps
- View logs: `docker-compose logs -f`
- Check health: `curl http://localhost:8000/health`

---

**Ready to go!** Access http://localhost:8000/docs to start using your microservices. 🎊
