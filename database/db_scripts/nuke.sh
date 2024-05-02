#!/usr/bin/env bash
set -e

container="$(docker container ls | grep 'postgres')"
stopped=""
if [ -n "$container" ]; then
  container=$(echo "$container" | rev | awk 'END {print $1}' | rev)
  stopped=$(docker stop "$container")
fi

if [ -n "$stopped" ]; then
  echo "Stopping container: $stopped"
else
  echo "No postgres container found running"
fi

sudo rm -rf /opt/docker-volumes/pgdata
