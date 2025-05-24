FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    # Database settings
    POSTGRES_SERVER=localhost \
    POSTGRES_DB=utm_db \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    # Superuser settings
    FIRST_SUPERUSER_EMAIL=admin@example.com \
    FIRST_SUPERUSER_PASSWORD=admin123 \
    FIRST_SUPERUSER_FULL_NAME="System Admin" \
    FIRST_SUPERUSER_IIN="123456789012" \
    # JWT settings
    SECRET_KEY="your-secret-key-here" \
    ACCESS_TOKEN_EXPIRE_MINUTES=30

# Install system dependencies
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

# Create start script with proper database initialization
RUN echo '#!/bin/bash\n\
service postgresql start\n\
su - postgres -c "createdb $POSTGRES_DB"\n\
sleep 5\n\
export DATABASE_URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_SERVER/$POSTGRES_DB"\n\
alembic upgrade head\n\
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]