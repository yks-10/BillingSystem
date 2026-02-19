# Microservices Implementation Guide

This guide will walk you through implementing the microservices architecture step by step.

## 📋 Overview

This implementation converts your monolithic billing system into 5 independent microservices:

1. **API Gateway** - Request routing
2. **Product Service** - Product management
3. **Order Service** - Order processing
4. **Denomination Service** - Cash management
5. **Notification Service** - Email notifications

## 🎯 Implementation Steps

### Phase 1: Setup and Preparation (15 minutes)

#### Step 1: Verify Prerequisites

```bash
# Check Docker
docker --version
docker-compose --version

# Check Python (for scripts)
python3 --version

# Check PostgreSQL client (optional, for manual DB access)
psql --version
```

#### Step 2: Navigate to Microservices Directory

```bash
cd /path/to/billing-system/microservices
```

#### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your email credentials (optional, for testing emails)
nano .env
```

For Gmail, you need an [App Password](https://support.google.com/accounts/answer/185833).

### Phase 2: Build and Start Services (10 minutes)

#### Step 4: Build Docker Images

```bash
# Build all services
docker-compose build

# This will:
# - Build 5 microservice images
# - Install Python dependencies
# - Copy shared modules
# - Set up health checks
```

#### Step 5: Start All Services

```bash
# Start services in background
docker-compose up -d

# Watch logs (optional)
docker-compose logs -f
```

Wait for all services to be healthy (30-60 seconds).

#### Step 6: Verify Services

```bash
# Check running services
docker-compose ps

# All services should show "Up (healthy)"

# Check aggregated health
curl http://localhost:8000/health | python3 -m json.tool
```

Expected output:
```json
{
  "gateway": "healthy",
  "services": {
    "products": "healthy",
    "billing": "healthy",
    "orders": "healthy",
    "denominations": "healthy",
    "notifications": "healthy"
  },
  "overall": "healthy"
}
```

### Phase 3: Seed Data (5 minutes)

#### Step 7: Install Script Dependencies

```bash
cd scripts
pip3 install -r requirements.txt
```

#### Step 8: Run Seed Script

```bash
python3 seed_data.py
```

This will create:
- 10 products (P001-P010)
- 10 denominations (₹2000 to ₹1)

### Phase 4: Testing (10 minutes)

#### Step 9: Access API Documentation

Open in browser:
- **API Gateway**: http://localhost:8000/docs
- **Product Service**: http://localhost:8001/docs
- **Order Service**: http://localhost:8002/docs
- **Denomination Service**: http://localhost:8003/docs
- **Notification Service**: http://localhost:8004/docs

#### Step 10: Test Individual Services

```bash
# Test Product Service
curl http://localhost:8001/products | python3 -m json.tool

# Test Denomination Service
curl http://localhost:8003/denominations | python3 -m json.tool
```

#### Step 11: Test Complete Order Flow

```bash
# Run automated test
cd scripts
python3 test_order_flow.py
```

Or manually test via API Gateway:

```bash
curl -X POST "http://localhost:8000/api/billing" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "test@example.com",
    "items": [
      {"product_id": "P001", "quantity": 1}
    ],
    "paid_amount": 60000.0
  }' | python3 -m json.tool
```

### Phase 5: Verify Complete Workflow

#### Step 12: Check Each Service Interaction

1. **Product Service** - Stock should be reduced
   ```bash
   curl http://localhost:8000/api/products/P001 | python3 -m json.tool
   # Check available_stock field
   ```

2. **Order Service** - Order should be created
   ```bash
   curl http://localhost:8000/api/orders/1 | python3 -m json.tool
   ```

3. **Denomination Service** - Change calculated
   ```bash
   curl -X POST "http://localhost:8000/api/denominations/calculate-change" \
     -H "Content-Type: application/json" \
     -d '{"amount": 1000}' | python3 -m json.tool
   ```

4. **Notification Service** - Check logs for email sending
   ```bash
   docker-compose logs notification-service | grep "Invoice"
   ```

5. **API Gateway** - All requests routed correctly
   ```bash
   docker-compose logs api-gateway | grep "Forwarding"
   ```

## 🛠️ Using Make Commands

For convenience, use the provided Makefile:

```bash
# Show all available commands
make help

# Start everything and seed data
make start-all

# Check health
make health

# View logs
make logs

# Run tests
make test

# Stop services
make down

# Clean everything
make clean
```

## 📊 Monitoring

### View Logs

```bash
# All services
make logs

# Specific service
make logs-product
make logs-order
make logs-gateway
```

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Access Databases Directly

```bash
# Product database (port 5433)
psql -h localhost -p 5433 -U postgres -d product_db

# Order database (port 5434)
psql -h localhost -p 5434 -U postgres -d order_db

# Denomination database (port 5435)
psql -h localhost -p 5435 -U postgres -d denomination_db
```

## 🔄 Development Workflow

### Making Changes

1. **Update code** in the service directory
2. **Rebuild** the specific service:
   ```bash
   docker-compose up -d --build product-service
   ```
3. **View logs** to verify:
   ```bash
   docker-compose logs -f product-service
   ```

### Debugging

```bash
# Stop a specific service
docker-compose stop product-service

# View its logs
docker-compose logs --tail=100 product-service

# Restart it
docker-compose start product-service

# Or restart with rebuild
docker-compose up -d --build product-service
```

### Testing Changes

```bash
# Run integration test after changes
cd scripts
python3 test_order_flow.py
```

## 🚀 Production Considerations

### Before Deploying to Production

1. **Security**
   - Change all default passwords
   - Enable HTTPS/TLS
   - Add authentication to API Gateway
   - Use secrets management (AWS Secrets Manager, Vault)

2. **Scalability**
   - Use Kubernetes for orchestration
   - Set up horizontal pod autoscaling
   - Add load balancer
   - Implement caching (Redis)

3. **Monitoring**
   - Add Prometheus + Grafana
   - Set up ELK stack for logging
   - Implement distributed tracing (Jaeger)
   - Set up alerts

4. **Reliability**
   - Add circuit breakers
   - Implement retry logic
   - Add request timeouts
   - Set up health checks

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check port conflicts
lsof -i :8000
lsof -i :8001
# etc.

# Remove old containers
docker-compose down
docker-compose up -d
```

### Database Connection Errors

```bash
# Restart databases
docker-compose restart product-db order-db denomination-db

# Check database health
docker-compose ps

# View database logs
docker-compose logs product-db
```

### Service Communication Issues

```bash
# Check network
docker network inspect billing-microservices

# Check if services can reach each other
docker-compose exec api-gateway curl http://product-service:8001/health
```

### Cleanup and Reset

```bash
# Stop and remove everything
make clean-all

# Rebuild from scratch
make rebuild

# Seed fresh data
make seed
```

## 📈 Performance Tips

1. **Database Connection Pooling**
   - Already configured in each service
   - Adjust pool size in `.env` if needed

2. **Async Operations**
   - Email sending is already async
   - Stock updates happen in background

3. **Caching**
   - Add Redis for product catalog
   - Cache denomination data
   - Cache frequent queries

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **Docker**: https://docs.docker.com/
- **Microservices Pattern**: https://microservices.io/
- **PostgreSQL**: https://www.postgresql.org/docs/

## ✅ Success Checklist

- [ ] All services started successfully
- [ ] Health check returns "healthy" for all services
- [ ] Seed data loaded successfully
- [ ] Can view products via API Gateway
- [ ] Can create orders successfully
- [ ] Stock is reduced after order
- [ ] Change is calculated correctly
- [ ] Email is sent (if configured)
- [ ] Can view order history
- [ ] API documentation accessible

## 🎉 Next Steps

Once everything is working:

1. Explore the API documentation at http://localhost:8000/docs
2. Try creating orders with different products
3. Check order history for different customers
4. Experiment with the denomination calculator
5. Add your own products and test
6. Try the automated test script multiple times

## 💡 Tips

- Use `docker-compose logs -f` to watch real-time logs
- Use the Swagger UI for interactive API testing
- Check the health endpoint regularly: http://localhost:8000/health
- Use Make commands for convenience: `make help`
- Keep the seed script handy for resetting data

---

**Congratulations!** You now have a fully functional microservices architecture running. 🎊

For questions or issues, refer to:
- [Main README](./README.md)
- [Architecture Documentation](../MICROSERVICES_ARCHITECTURE.md)
- Service-specific logs: `docker-compose logs [service-name]`
