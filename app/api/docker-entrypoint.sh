#!/bin/sh
set -e
APP="form-services"
echo "Running App: ${APP}"
export FLASK_APP="$APP"

python3 -m main