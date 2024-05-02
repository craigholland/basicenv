#!/bin/bash
# Run this from the services directory

export PYTHONPATH=.
source .venv/bin/activate

DB_NAME=`uuidgen`
COMMIT_NAME="${1}"
FLAGS="${2}"

DB_HOST=${POSTGRES_HOST:-127.0.0.1}
DB_PORT=${POSTGRES_PORT:-5432}
DB_USER=${POSTGRES_USER:-postgres}
#cd ../
#psql -U $DB_USER -h $DB_HOST -p ${DB_PORT} -d postgres -c "CREATE DATABASE \"${DB_NAME}\""

#export DATABASE_URL="postgresql://${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"


alembic upgrade head
alembic revision $FLAGS -m "${COMMIT_NAME}"
