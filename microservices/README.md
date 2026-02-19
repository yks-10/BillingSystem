# Billing System - Microservices Architecture

This is the microservices implementation of the billing system, breaking down the monolithic application into independent, scalable services.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Services](#services)
- [Quick Start](#quick-start)
- [Running Without Docker](#running-without-docker)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Migration from Monolith](#migration-from-monolith)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   API Gateway   │ (Port 8000) - Entry point for all requests
└────────┬────────┘
         │
    ┌────┴────────────────────────┐
    │                             │
┌───▼──────────┐    ┌────────────▼───┐
│   Product    │    │  Order/Billing │
│   Service    │◄───┤    Service     │
│  (Port 8001) │    │   (Port 8002)  │
└──────────────┘    └────────┬───────┘
                             │
                    ┌────────┴────────┐
                    │                 │
         ┌──────────▼─────┐  ┌───────▼────────┐
         │  Denomination  │  │ Notification   │
         │    Service     │  │    Service     │
         │  (Port 8003)   │  │  (Port 8004)   │
         └────────────────┘  └────────────────┘
```

## 📦 Services

### 1. **API Gateway** (Port 8000)
- Single entry point for all client requests
- Routes requests to appropriate microservices
- Health check aggregation

### 2. **Product Service** (Port 8001)
- Product CRUD operations
- Stock management
- Stock availability checks
- Database: `product_db`

### 3. **Order Service** (Port 8002)
- Order creation and billing
- Order history
- Orchestrates Product, Denomination, and Notification services
- Database: `order_db`

### 4. **Denomination Service** (Port 8003)
- Denomination management
- Change calculation using greedy algorithm
- Database: `denomination_db`

### 5. **Notification Service** (Port 8004)
- Email notifications
- Invoice generation and sending
- No database required (stateless)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- (Optional) For email: Gmail account with App Password

### 1. Clone and Navigate

```bash
cd /path/to/billing-system/microservices
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your email credentials (optional)
nano .env
```

### 3. Start All Services

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

This will start:
- 3 PostgreSQL databases (ports 5433, 5434, 5435)
- 5 microservices (ports 8000-8004)

### 4. Verify Services

```bash
# Check all services are running
docker-compose ps

# Check health
curl http://localhost:8000/health
```

### 5. Access API Documentation

- **API Gateway Swagger**: http://localhost:8000/docs
- **Product Service**: http://localhost:8001/docs
- **Order Service**: http://localhost:8002/docs
- **Denomination Service**: http://localhost:8003/docs
- **Notification Service**: http://localhost:8004/docs

### 6. Seed Initial Data

```bash
# Seed products
curl -X POST "http://localhost:8000/api/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "P001",
    "name": "Laptop",
    "price": 50000.00,
    "tax_percentage": 18.0,
    "available_stock": 10
  }'

# Seed denominations
curl -X POST "http://localhost:8000/api/denominations" \
  -H "Content-Type: application/json" \
  -d '{
    "value": 500,
    "available_count": 100
  }'
```

### 7. Create a Test Order

```bash
curl -X POST "http://localhost:8000/api/billing" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "customer@example.com",
    "items": [
      {"product_id": "P001", "quantity": 1}
    ],
    "paid_amount": 60000.00
  }'
```

## 🖥️ Running Without Docker

If you prefer to run services locally without Docker:

### Prerequisites

- Python 3.12+
- PostgreSQL 15+

### Setup

#### 1. Create Databases

```sql
CREATE DATABASE product_db;
CREATE DATABASE order_db;
CREATE DATABASE denomination_db;
```

#### 2. Set Up Each Service

For each service (product-service, order-service, etc.):

```bash
# Navigate to service directory
cd product-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example app/.env
nano app/.env  # Edit with your settings

# Run service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

#### 3. Start Services in Order

Start services in this order (separate terminals):

1. Product Service (Port 8001)
2. Denomination Service (Port 8003)
3. Notification Service (Port 8004)
4. Order Service (Port 8002)
5. API Gateway (Port 8000)

## 📚 API Documentation

### Product Service Endpoints

```bash
# Create product
POST /products

# List products
GET /products?skip=0&limit=100

# Get product
GET /products/{product_id}

# Update product
PUT /products/{product_id}

# Delete product
DELETE /products/{product_id}

# Check stock
POST /products/check-stock

# Update stock
POST /products/update-stock
```

### Order Service Endpoints

```bash
# Create order/bill
POST /billing

# List orders
GET /orders?skip=0&limit=100

# Get order details
GET /orders/{order_id}

# Get customer orders
GET /orders/customer/{email}
```

### Denomination Service Endpoints

```bash
# Create denomination
POST /denominations

# List denominations
GET /denominations

# Get denomination
GET /denominations/{id}

# Update denomination
PUT /denominations/{id}

# Delete denomination
DELETE /denominations/{id}

# Calculate change
POST /denominations/calculate-change
```

### Notification Service Endpoints

```bash
# Send invoice email
POST /notifications/email/invoice

# Send generic email
POST /notifications/email/generic
```

## 🧪 Testing

### Manual Testing

#### 1. Test Product Service

```bash
# Create product
curl -X POST "http://localhost:8000/api/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "P001",
    "name": "Test Product",
    "price": 100.0,
    "tax_percentage": 18.0,
    "available_stock": 50
  }'

# Get all products
curl "http://localhost:8000/api/products"

# Get specific product
curl "http://localhost:8000/api/products/P001"
```

#### 2. Test Denomination Service

```bash
# Create denominations
for value in 2000 500 200 100 50 20 10 5 2 1; do
  curl -X POST "http://localhost:8000/api/denominations" \
    -H "Content-Type: application/json" \
    -d "{\"value\": $value, \"available_count\": 100}"
done

# Calculate change
curl -X POST "http://localhost:8000/api/denominations/calculate-change" \
  -H "Content-Type: application/json" \
  -d '{"amount": 1234}'
```

#### 3. Test Order Flow

```bash
# Create complete order
curl -X POST "http://localhost:8000/api/billing" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "test@example.com",
    "items": [
      {"product_id": "P001", "quantity": 2}
    ],
    "paid_amount": 300.0
  }'

# Check order history
curl "http://localhost:8000/api/orders/customer/test@example.com"
```

### Integration Testing Script

Create `test_microservices.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api"

echo "1. Creating product..."
curl -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "TEST001",
    "name": "Test Item",
    "price": 100.0,
    "tax_percentage": 18.0,
    "available_stock": 10
  }'

echo -e "\n\n2. Creating denominations..."
curl -X POST "$BASE_URL/denominations" \
  -H "Content-Type: application/json" \
  -d '{"value": 100, "available_count": 50}'

echo -e "\n\n3. Creating order..."
curl -X POST "$BASE_URL/billing" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "test@example.com",
    "items": [{"product_id": "TEST001", "quantity": 1}],
    "paid_amount": 200.0
  }'

echo -e "\n\nTests completed!"
```

Run: `chmod +x test_microservices.sh && ./test_microservices.sh`

## 🔄 Migration from Monolith

### Data Migration

If migrating from the existing monolithic application:

#### 1. Export Data from Monolith

```bash
# Export products
psql billing_db -c "\COPY products TO '/tmp/products.csv' CSV HEADER"

# Export orders
psql billing_db -c "\COPY orders TO '/tmp/orders.csv' CSV HEADER"

# Export order_items
psql billing_db -c "\COPY order_items TO '/tmp/order_items.csv' CSV HEADER"

# Export denominations
psql billing_db -c "\COPY denominations TO '/tmp/denominations.csv' CSV HEADER"
```

#### 2. Import to Microservices

```bash
# Import products
psql -h localhost -p 5433 -U postgres product_db -c "\COPY products FROM '/tmp/products.csv' CSV HEADER"

# Import orders and order_items
psql -h localhost -p 5434 -U postgres order_db -c "\COPY orders FROM '/tmp/orders.csv' CSV HEADER"
psql -h localhost -p 5434 -U postgres order_db -c "\COPY order_items FROM '/tmp/order_items.csv' CSV HEADER"

# Import denominations
psql -h localhost -p 5435 -U postgres denomination_db -c "\COPY denominations FROM '/tmp/denominations.csv' CSV HEADER"
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check logs
docker-compose logs -f [service-name]

# Check if ports are available
lsof -i :8000  # Check each port

# Restart services
docker-compose restart
```

#### 2. Database Connection Errors

```bash
# Check database status
docker-compose ps

# Restart databases
docker-compose restart product-db order-db denomination-db

# Check database logs
docker-compose logs product-db
```

#### 3. Service Communication Errors

```bash
# Check if all services are healthy
curl http://localhost:8000/health

# Verify network
docker network inspect billing-microservices

# Check individual service
curl http://localhost:8001/health  # Product service
curl http://localhost:8002/health  # Order service
```

#### 4. Email Not Sending

```bash
# Check notification service logs
docker-compose logs notification-service

# Verify email configuration in .env file
# For Gmail, ensure you're using an App Password
```

### Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f product-service

# Recent logs
docker-compose logs --tail=100
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## 🔐 Security Considerations

1. **Change default passwords** in production
2. **Use environment variables** for sensitive data
3. **Enable authentication** on API Gateway
4. **Use HTTPS** in production
5. **Implement rate limiting**
6. **Add API key validation**

## 🚀 Next Steps

1. **Add Authentication**: Implement JWT authentication in API Gateway
2. **Add Caching**: Redis for frequently accessed data
3. **Add Message Queue**: RabbitMQ/Kafka for async operations
4. **Add Service Discovery**: Consul or Kubernetes service discovery
5. **Add Monitoring**: Prometheus + Grafana
6. **Add Tracing**: Jaeger for distributed tracing
7. **Add CI/CD**: GitHub Actions or Jenkins

## 📄 Additional Documentation

- [Architecture Details](../MICROSERVICES_ARCHITECTURE.md)
- [Individual Service READMEs](./product-service/README.md)
- [Original Monolith README](../README.md)

## 💡 Tips

- Use `docker-compose up -d` to run in background
- Use `docker-compose ps` to check service status
- Access Swagger UI for interactive API testing
- Check health endpoint regularly: `/health`
- Monitor logs during development

## 🤝 Contributing

When adding new features:
1. Update shared schemas if needed
2. Add comprehensive error handling
3. Update API documentation
4. Add health checks
5. Update docker-compose.yml

---

**Questions?** Check the main [MICROSERVICES_ARCHITECTURE.md](../MICROSERVICES_ARCHITECTURE.md) for detailed architecture information.
