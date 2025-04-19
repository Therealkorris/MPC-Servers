.PHONY: setup test backend mpc help docker-build docker-run docker-stop

# Default target
help:
	@echo "Available commands:"
	@echo "  setup     - Install dependencies"
	@echo "  test      - Run tests"
	@echo "  backend   - Run the backend server only"
	@echo "  mpc       - Run the MPC server"
	@echo "  docker-build - Build the Docker image"
	@echo "  docker-run   - Run the Docker container"
	@echo "  docker-stop  - Stop the Docker container"
	@echo "  help      - Show this help message"

# Setup the environment
setup:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Run tests
test:
	@echo "Running tests..."
	cd src/backend && python run_tests.py -v

# Run the backend server
backend:
	@echo "Starting backend server..."
	python src/run_mpc.py --backend-only --reload

# Run the MPC server
mpc:
	@echo "Starting MPC server..."
	python src/run_mpc.py --transport sse 

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t mpc-visio-server .

docker-run:
	@echo "Running Docker container..."
	docker compose up -d

docker-stop:
	@echo "Stopping Docker container..."
	docker compose down 