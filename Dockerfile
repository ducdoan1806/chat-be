# Dockerfile
# Multi-stage: build static + package, then runtime
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install build deps for mysqlclient and common libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements first to leverage cache
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

# Collect static files (Django settings must be configured to use STATIC_ROOT)
ENV DJANGO_SETTINGS_MODULE=chat_be.settings_prod
RUN python manage.py collectstatic --noinput

# Final runtime image (smaller)
FROM python:3.12-slim

WORKDIR /app

# runtime deps (client libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/*




# Copy site packages from builder's pip installs
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# Copy application
COPY --from=builder /app /app

# Copy startup scripts
COPY ./entrypoint.sh /entrypoint.sh
COPY ./wait-for-db.sh /wait-for-db.sh
RUN chmod +x /entrypoint.sh /wait-for-db.sh

# Nginx config (to be mounted or copied)
COPY ./nginx.conf /etc/nginx/nginx.conf

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
