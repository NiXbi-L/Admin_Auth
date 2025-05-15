#!/bin/bash

# Ожидание запуска PostgreSQL
echo "Ожидание запуска PostgreSQL..."
sleep 5

# Применение миграций
echo "Применение миграций..."
python manage.py migrate

# Создание суперпользователя, если переменные окружения заданы
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Создание суперпользователя..."
    python manage.py createsuperuser --noinput
fi

# Запуск сервера через Gunicorn
echo "Запуск сервера..."
exec gunicorn Admin_Auth.wsgi:application --bind 0.0.0.0:8000 