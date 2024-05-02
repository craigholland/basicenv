#!/usr/bin/env bash
# execute with the dot-space method in order to export env variable
# $>. ./start.sh

container_id=$( \
  docker run -d --rm --name testdb --net=host \
  -e POSTGRES_DB=localpg \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v /opt/docker-volumes/pgdata:/var/lib/postgresql/data \
  debezium/postgres:12 postgres -c log_statement=all \
)
if [ -n "$container_id" ]; then
  echo "Postgres Docker container 'testdb' started (id: $container_id):"
  echo " Database name: localpg"
  echo " Database user: postgres"
  echo " Database pwd: postgres"

  export DATABASE_URL=postgresql://postgres@localhost:5432/localpg
  echo "Exported: DATABASE_URL=postgresql://postgres@localhost:5432/localpg"

fi


