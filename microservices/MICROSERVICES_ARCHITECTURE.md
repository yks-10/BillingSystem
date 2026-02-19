# Microservices Architecture - Billing System

## Overview
This document outlines the microservices architecture for the billing system, breaking down the monolithic application into independent, scalable services.

## Architecture Components

### 1. API Gateway (Port 8000)
- **Purpose**: Single entry point for all client requests
- **Responsibilities**:
  - Route requests to appropriate microservices
  - Handle authentication/authorization (future)
  - Request/response transformation
  - Load balancing
  - Rate limiting

### 2. Product Service (Port 8001)
- **Purpose**: Manage product catalog
- **Responsibilities**:
  - CRUD operations for products
  - Stock management
  - Product validation
  - Product search and filtering
- **Database**: `product_db` (Products table)
- **Endpoints**:
  - `POST /products` - Create product
  - `GET /products` - List products
  - `GET /products/{id}` - Get product
  - `PUT /products/{id}` - Update product
  - `DELETE /products/{id}` - Delete product
  - `POST /products/check-stock` - Check stock availability

### 3. Order/Billing Service (Port 8002)
- **Purpose**: Handle order creation and billing
- **Responsibilities**:
  - Process billing requests
  - Create orders and order items
  - Calculate taxes and totals
  - Orchestrate other services (products, denominations, notifications)
  - Manage order history
- **Database**: `order_db` (Orders, OrderItems tables)
- **Endpoints**:
  - `POST /billing` - Create bill/order
  - `GET /orders` - List orders
  - `GET /orders/{id}` - Get order details
  - `GET /orders/customer/{email}` - Get customer orders

### 4. Denomination Service (Port 8003)
- **Purpose**: Manage cash denominations and change calculation
- **Responsibilities**:
  - CRUD operations for denominations
  - Calculate optimal change using greedy algorithm
  - Track available denomination counts
- **Database**: `denomination_db` (Denominations table)
- **Endpoints**:
  - `POST /denominations` - Create denomination
  - `GET /denominations` - List denominations
  - `PUT /denominations/{id}` - Update denomination
  - `DELETE /denominations/{id}` - Delete denomination
  - `POST /denominations/calculate` - Calculate change

### 5. Notification Service (Port 8004)
- **Purpose**: Handle all outbound notifications
- **Responsibilities**:
  - Send invoice emails
  - Format email templates
  - Queue management for async sending
  - Email delivery tracking (future)
- **Database**: `notification_db` (optional for tracking)
- **Endpoints**:
  - `POST /notifications/email/invoice` - Send invoice email
  - `POST /notifications/email/generic` - Send generic email

## Communication Patterns

### Synchronous (REST API)
- API Gateway ↔ All Services
- Order Service → Product Service (stock check, stock update)
- Order Service → Denomination Service (calculate change)
- Order Service → Notification Service (send email)

### Asynchronous (Future Enhancement)
- Message Queue (RabbitMQ/Kafka) for:
  - Order events
  - Email notifications
  - Stock updates

## Database Strategy

### Option 1: Database per Service (Recommended)
Each service has its own PostgreSQL database:
- `product_db`
- `order_db`
- `denomination_db`
- `notification_db`

**Pros**: True service independence, easier scaling
**Cons**: More complex data management, eventual consistency

### Option 2: Shared Database with Schema Separation
Single PostgreSQL instance with separate schemas:
- `product_schema`
- `order_schema`
- `denomination_schema`

**Pros**: Simpler setup, ACID transactions
**Cons**: Tight coupling, harder to scale independently

## Service Discovery

For development, use hardcoded service URLs in environment variables.

For production, consider:
- **Consul** - Service registry and health checks
- **Kubernetes Service Discovery** - If using K8s
- **AWS Service Discovery** - If on AWS

## Deployment Strategy

### Docker Containerization
Each service runs in its own Docker container with:
- Python 3.12 base image
- Service-specific dependencies
- Health check endpoints
- Environment-based configuration

### Docker Compose (Development)
All services orchestrated with docker-compose for local development.

### Kubernetes (Production)
- Separate deployments for each service
- Service mesh (Istio) for inter-service communication
- Horizontal Pod Autoscaling
- Ingress for API Gateway

## Configuration Management

### Environment Variables
Each service configured via `.env` file:
```env
SERVICE_NAME=product-service
SERVICE_PORT=8001
DATABASE_URL=postgresql://user:pass@host:5432/product_db
API_GATEWAY_URL=http://localhost:8000
PRODUCT_SERVICE_URL=http://localhost:8001
ORDER_SERVICE_URL=http://localhost:8002
DENOMINATION_SERVICE_URL=http://localhost:8003
NOTIFICATION_SERVICE_URL=http://localhost:8004
```

## Migration Path

### Phase 1: Service Extraction
1. ✅ Create separate directories for each service
2. ✅ Extract service-specific code
3. ✅ Create individual FastAPI apps
4. ✅ Set up service-to-service communication

### Phase 2: Database Separation
1. Create separate databases
2. Migrate data
3. Update connection strings
4. Test data isolation

### Phase 3: Containerization
1. Create Dockerfiles for each service
2. Create docker-compose.yml
3. Test container orchestration

### Phase 4: API Gateway Implementation
1. Set up gateway routing
2. Implement request forwarding
3. Add authentication/authorization
4. Add rate limiting

### Phase 5: Production Deployment
1. Set up Kubernetes cluster
2. Create deployment manifests
3. Configure service mesh
4. Set up monitoring and logging

## Security Considerations

1. **Service-to-Service Authentication**
   - API keys or JWT tokens
   - mTLS for production

2. **Network Security**
   - Private network for inter-service communication
   - Expose only API Gateway publicly

3. **Data Encryption**
   - TLS for all communications
   - Database encryption at rest

4. **Secret Management**
   - Use vault (HashiCorp Vault, AWS Secrets Manager)
   - Never commit secrets to version control

## Monitoring & Observability

1. **Logging**
   - Centralized logging (ELK Stack, CloudWatch)
   - Structured JSON logs
   - Correlation IDs for request tracing

2. **Metrics**
   - Prometheus + Grafana
   - Service-specific metrics
   - System metrics (CPU, memory, network)

3. **Tracing**
   - Distributed tracing (Jaeger, Zipkin)
   - Request flow visualization
   - Performance bottleneck identification

4. **Health Checks**
   - Liveness probes
   - Readiness probes
   - Dependency health checks

## Scalability

### Horizontal Scaling
- Each service can scale independently
- Load balancer distributes requests
- Auto-scaling based on metrics

### Caching Strategy
- Redis for frequently accessed data
- Product catalog caching
- Denomination data caching

### Database Optimization
- Connection pooling
- Read replicas for read-heavy services
- Database indexing optimization

## Testing Strategy

1. **Unit Tests** - Test individual service logic
2. **Integration Tests** - Test service interactions
3. **Contract Tests** - Verify API contracts between services
4. **End-to-End Tests** - Test complete user flows
5. **Load Tests** - Test scalability and performance

## Cost Considerations

- More infrastructure complexity = higher ops cost
- Multiple databases = more management overhead
- Consider serverless options (AWS Lambda, Cloud Run) for notification service
- Use managed services where possible (RDS, ElastiCache)

## When NOT to Use Microservices

If your application:
- Has a small team (< 5 developers)
- Low traffic (< 10 req/s)
- Simple business logic
- No need for independent scaling

Then a **modular monolith** might be better!

## Next Steps

See `MICROSERVICES_IMPLEMENTATION.md` for step-by-step implementation guide.
