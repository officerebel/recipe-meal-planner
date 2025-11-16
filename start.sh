#!/bin/bash
cd backend
export PYTHONPATH="/app/backend:$PYTHONPATH"

# Wait for database to be ready
echo "Waiting for database..."
max_retries=30
retry_count=0
until python manage.py migrate --check 2>/dev/null || [ $retry_count -eq $max_retries ]; do
  echo "Database not ready yet, waiting... (attempt $((retry_count+1))/$max_retries)"
  sleep 2
  retry_count=$((retry_count+1))
done

if [ $retry_count -eq $max_retries ]; then
  echo "Database connection timeout after $max_retries attempts"
  exit 1
fi

echo "Database is ready, running migrations..."
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn recipe_meal_planner.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2