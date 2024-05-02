#!/usr/bin/env bash
# This script migrates a database to the latest version
# It requires a single parameter, the URL of the database

export PYTHONPATH=.
if [ -z "$1" ]; then
  if [ -z "$DATABASE_URL" ]; then
    echo "usage: migrate_database.sh DATABASE_URL"
    echo "Run '. ./start_db.sh' if the Docker container is not yet running to get DATABASE_URL"
    exit
  fi
else
  export DATABASE_URL=$1
fi

alembic upgrade head
