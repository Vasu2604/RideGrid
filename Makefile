.PHONY: help dev-up dev-down build test lint clean install proto

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	@echo "Installing Python dependencies..."
	pip install -r backend/requirements.txt
	pip install -e libs/ridegrid-common
	@echo "Installing frontend dependencies..."
	cd web/ops-console && npm install
	@echo "✓ Dependencies installed"

proto: ## Generate protobuf code
	@echo "Generating protobuf code..."
	python -m grpc_tools.protoc --proto_path=proto \
		--python_out=libs/ridegrid-proto/ridegrid_proto \
		--grpc_python_out=libs/ridegrid-proto/ridegrid_proto \
		--pyi_out=libs/ridegrid-proto/ridegrid_proto \
		proto/ridegrid.proto
	@echo "✓ Protobuf code generated"

dev-up: ## Start development environment
	@echo "Starting development environment..."
	cd deploy/docker-compose && docker-compose up -d
	@echo "✓ Development environment started"
	@echo ""
	@echo "Services available at:"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - Gateway API: http://localhost:8001"
	@echo "  - State Query API: http://localhost:8003"
	@echo "  - Grafana: http://localhost:3001 (admin/admin)"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Kafka UI: http://localhost:8080"

dev-down: ## Stop development environment
	@echo "Stopping development environment..."
	cd deploy/docker-compose && docker-compose down
	@echo "✓ Development environment stopped"

dev-logs: ## Show development logs
	cd deploy/docker-compose && docker-compose logs -f

lint: ## Run linters
	@echo "Running Python linters..."
	ruff check .
	black --check .
	isort --check-only .
	@echo "Running frontend linter..."
	cd web/ops-console && npm run lint
	@echo "✓ Linting complete"

format: ## Format code
	@echo "Formatting Python code..."
	black .
	isort .
	@echo "✓ Code formatted"

typecheck: ## Run type checking
	@echo "Running mypy..."
	mypy services/ libs/ --ignore-missing-imports
	@echo "✓ Type checking complete"

test: ## Run all tests
	@echo "Running unit tests..."
	pytest tests/ -v --cov=services --cov-report=term-missing
	@echo "✓ Tests complete"

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	pytest tests/test_gateway.py -v
	@echo "✓ Integration tests complete"

load-test: ## Run load tests
	@echo "Running k6 load test..."
	k6 run load/k6/load-test.js
	@echo "✓ Load test complete"

build: ## Build Docker images
	@echo "Building Docker images..."
	docker build -t ridegrid/gateway:latest services/gateway
	docker build -t ridegrid/telemetry-ingest:latest services/telemetry-ingest
	docker build -t ridegrid/matching-engine:latest services/matching-engine
	docker build -t ridegrid/assignment-orchestrator:latest services/assignment-orchestrator
	docker build -t ridegrid/state-query:latest services/state-query
	docker build -t ridegrid/ops-console:latest web/ops-console
	@echo "✓ Docker images built"

deploy-k8s: ## Deploy to Kubernetes
	@echo "Deploying to Kubernetes..."
	helm upgrade --install ridegrid helm/ridegrid \
		--create-namespace \
		--namespace ridegrid
	@echo "✓ Deployed to Kubernetes"

clean: ## Clean generated files and caches
	@echo "Cleaning..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	@echo "✓ Cleaned"

seed-data: ## Seed database with test data
	@echo "Seeding database..."
	python scripts/seed_data.py
	@echo "✓ Database seeded"

dashboard: ## Open Grafana dashboard
	@echo "Opening Grafana..."
	open http://localhost:3001

docs: ## Generate documentation
	@echo "Documentation available at:"
	@echo "  - README: ./README.md"
	@echo "  - Architecture: ./docs/architecture.md"
	@echo "  - API Docs: ./docs/api.md"
	@echo "  - Runbook: ./docs/runbook.md"





