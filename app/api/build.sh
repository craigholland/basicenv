#!/bin/sh

set -e

GCAR_IO=${GCAR_IO:-"local"}
GCP_PROJECT_ID=${GCP_PROJECT_ID:-"local"}

TAG="cholland/servicestest"
VERSION="1.0.2"
REPO="${GCAR_IO}/${GCP_PROJECT_ID}"

# Create docker repo
if test -d dockerbuild; then
  echo "Updating old dockerbuild directory...\n"
  rm -rf dockerbuild
fi
mkdir dockerbuild

# Make symlinks to external modules
old=$*
set -- "domain" "database"
cd ../../
pwd=`pwd`
cd app
for mod in "$@"; do
  if [ -L "$mod" ] && [ -d "$mod" ]; then
    rm "$mod"
  fi

  ln -s "$pwd/$mod" "$mod"
  if [ -L "$mod" ] && [ -d "$mod" ]; then
    echo "Symlink /app/$mod created..."
    rsync -av "$mod" "api/dockerbuild" --exclude .venv --exclude .idea --copy-links
    echo "Syncing symlink '$mod' with dockerbuild directory..."
  fi
  echo "\n"
done
cd api
# Restore arguments
eval "set -- $old"


docker build --tag="${REPO}/${TAG}:${VERSION}" .
#
#docker stop servicestest
#docker system prune -a
#docker build . -t servicestest:1.0.2
#docker run -d -p 8081:8081 --name=servicestest servicestest:1.0.2