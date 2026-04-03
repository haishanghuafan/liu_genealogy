FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir pip --upgrade && \
    pip install --no-cache-dir .

# Copy application code
COPY . .

# Expose port
EXPOSE 8010

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
