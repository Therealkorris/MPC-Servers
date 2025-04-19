.PHONY: setup test backend mpc help

# Default target
help:
	@echo "Available commands:"
	@echo "  setup     - Install dependencies"
	@echo "  test      - Run tests"
	@echo "  backend   - Run the backend server only"
	@echo "  mpc       - Run the MPC server"
	@echo "  help      - Show this help message"

# Setup the environment
setup:
	@echo "Installing dependencies..."
	pip install -r src/backend/requirements.txt

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