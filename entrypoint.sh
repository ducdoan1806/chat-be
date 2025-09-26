
#!/usr/bin/env bash
set -e

# Wait DB ready
./wait-for-db.sh ${SQL_HOST:-db} ${SQL_PORT:-3306} 60

# Collect static (already done in build, but safe)
python manage.py collectstatic --noinput

# Run migrations (production: cân nhắc quản lý migrations từ CI/CD; ở đây thực hiện 1 lần)
python manage.py migrate --noinput

# Create superuser if provided via env (optional)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput || true
fi

# Start Gunicorn (bind to unix socket or 0.0.0.0:8000)
# Use number of workers = 2 * CPU + 1 (simple heuristic)
GUNICORN_CMD="gunicorn chat_be.wsgi:application --bind unix:/tmp/gunicorn.sock --workers ${GUNICORN_WORKERS:-3} --access-logfile -"

# Start nginx in foreground and Gunicorn
# Start gunicorn in background, then nginx in foreground
eval $GUNICORN_CMD &

# nginx must be foreground: use -g 'daemon off;'
nginx -g 'daemon off;'
