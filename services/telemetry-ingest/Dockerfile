FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy shared libraries first
COPY libs/ridegrid-common /app/libs/ridegrid-common
COPY libs/ridegrid-proto /app/libs/ridegrid-proto

# Install shared libraries
RUN pip install --no-cache-dir -e /app/libs/ridegrid-common

# Copy service requirements and install
COPY services/telemetry-ingest/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/telemetry-ingest/ .

# Expose gRPC port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]

