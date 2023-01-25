#!/bin/sh

if ["$DATABASE" = "postgres"]
then
    echo "Waiting for response..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL Started!"

fi

# python manage.py flush --no-input
python manage.py makemigrations --no-input
python manage.py migrate --no-input
# python manage.py collectstatic --no-input --clear
rm celerybeat.pid
rm logs/debug.log

exec "$@"