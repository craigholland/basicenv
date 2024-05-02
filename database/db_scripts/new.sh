#!/bin/bash
# Run this from the services directory

export PYTHONPATH=.
source .venv/bin/activate
set -e

if [ -z $1 ]; then
	DB_NAME=$(uuidgen)
else
	DB_NAME=$1
fi


DB_HOST=${POSTGRES_HOST:-127.0.0.1}
DB_PORT=${POSTGRES_PORT:-5432}
DB_USER=${POSTGRES_USER:-postgres}
DB_PASSWORD=${POSTGRES_PASSWORD:-postgres}
psql -U $DB_USER -h $DB_HOST -p ${DB_PORT} -d postgres -c "CREATE DATABASE \"${DB_NAME}\""

export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
alembic upgrade head
echo "Your Database URL: ${DATABASE_URL}"
echo "Your Database Name: ${DB_NAME}"
