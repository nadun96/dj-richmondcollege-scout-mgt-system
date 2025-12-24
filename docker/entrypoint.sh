#!/bin/sh
set -o errexit
set -o pipefail
set -o nounset

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec gunicorn zeta.wsgi:application --bind 0.0.0.0:8000
