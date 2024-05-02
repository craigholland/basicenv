#!/bin/sh
set -e
APP="form-services"
echo "Running App: ${APP}"
export FLASK_APP="$APP"
#gunicorn -b 0.0.0.0:8081 --preload $FLASK_APP
python3 -m main