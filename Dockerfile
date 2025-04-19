FROM python:3.11-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better layer caching
COPY src/backend/requirements.txt ./requirements.txt

# Create a filtered requirements file without fictitious packages
RUN grep -v "fictitious package" requirements.txt | grep -v "pyvismx" | grep -v "ollama-python" > requirements.filtered.txt

# Install dependencies with compatible versions
RUN pip install --upgrade pip setuptools==59.6.0 wheel && \
    pip install --no-cache-dir -r requirements.filtered.txt && \
    pip install sse-starlette requests

# Copy the server code
COPY src/backend/server.py ./backend/server.py
COPY src/backend/api ./backend/api/
COPY src/backend/main.py ./backend/main.py
COPY src/backend/ollama_service.py ./backend/ollama_service.py
COPY src/backend/docker_visio_service.py ./backend/visio_service.py
COPY src/run_mpc.py ./run_mpc.py

# Create required directories
RUN mkdir -p backend/uploads

# Expose the port used by the SSE transport
EXPOSE 8050

# Environment variables
ENV HOST=0.0.0.0
ENV PORT=8050
ENV TRANSPORT=sse
ENV LOCAL_VISIO_SERVICE=http://host.docker.internal:8051
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/health || exit 1

# Command to run the MPC server with SSE transport
CMD ["python", "run_mpc.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "8050"] 