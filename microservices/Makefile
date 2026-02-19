# Makefile for Microservices Management

.PHONY: help build up down restart logs clean seed test health

help: ## Show this help message
	@echo "Microservices Management Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "✅ All services started!"
	@echo "🌐 API Gateway: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs from all services
	docker-compose logs -f

logs-gateway: ## View API Gateway logs
	docker-compose logs -f api-gateway

logs-product: ## View Product Service logs
	docker-compose logs -f product-service

logs-order: ## View Order Service logs
	docker-compose logs -f order-service

logs-denom: ## View Denomination Service logs
	docker-compose logs -f denomination-service

logs-notif: ## View Notification Service logs
	docker-compose logs -f notification-service

clean: ## Stop services and remove volumes
	docker-compose down -v
	@echo "✅ All services stopped and data removed"

clean-all: ## Stop services, remove volumes and images
	docker-compose down -v --rmi all
	@echo "✅ Everything cleaned up"

ps: ## Show running services
	docker-compose ps

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ Services not responding"

seed: ## Seed initial data (requires services to be running)
	@echo "🌱 Seeding data..."
	@cd scripts && python3 seed_data.py

test: ## Run order flow test
	@echo "🧪 Testing order flow..."
	@cd scripts && python3 test_order_flow.py

dev-setup: ## Setup for local development (without Docker)
	@echo "Setting up local development environment..."
	@for service in product-service order-service denomination-service notification-service api-gateway; do \
		echo "Setting up $$service..."; \
		cd $$service && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && cd ..; \
	done
	@echo "✅ Development environment ready"

start-all: up seed ## Start services and seed data
	@echo "✅ Services started and data seeded"
	@echo "🚀 Ready to use!"

rebuild: clean build up ## Clean rebuild all services
	@echo "✅ Services rebuilt and started"
