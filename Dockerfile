FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=80 \
    POSTGRES_DB=utm_db \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres

# Install system dependencies and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    postgresql \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copy application code
COPY . .

# Initialize PostgreSQL and create start script
RUN echo '#!/bin/bash\n\
service postgresql start\n\
su - postgres -c "createdb $POSTGRES_DB"\n\
sleep 5\n\
alembic upgrade head\n\
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]