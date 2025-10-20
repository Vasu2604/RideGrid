FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared libraries first
COPY libs/ridegrid-common /app/libs/ridegrid-common
COPY libs/ridegrid-proto /app/libs/ridegrid-proto

# Install shared libraries
RUN pip install --no-cache-dir -e /app/libs/ridegrid-common

# Copy service requirements and install
COPY services/gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/gateway/ .

# Expose ports
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

