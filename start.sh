#!/bin/bash
cd backend
export PYTHONPATH="/app/backend:$PYTHONPATH"
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn recipe_meal_planner.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2