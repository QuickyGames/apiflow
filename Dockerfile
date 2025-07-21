# Backend Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Create a startup script
RUN echo '#!/bin/bash\n\
if [ "$SERVICE_TYPE" = "worker" ]; then\n\
    echo "Starting worker..."\n\
    python -m backend.worker\n\
else\n\
    echo "Starting API server..."\n\
    uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload\n\
fi' > /app/start.sh && chmod +x /app/start.sh

# Expose port for API
EXPOSE 8000

# Run the startup script
CMD ["/app/start.sh"]
