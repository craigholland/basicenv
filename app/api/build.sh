#!/bin/sh
usage() { echo "usage comment"; exit 1;}
bool(){ return "$((!${#1}))"; }

set -e
REPO=${DEFAULT_CONTAINER_REPO:-""}
TAG=${DEFAULT_CONTAINER_TAG:-""}
GCP_AR_ID=${GCP_AR_ID:-""}
GCP_PROJECT_ID=${GCP_PROJECT_ID:-""}
GCP_REGION=${GCP_REGION:-""}

GCP=false
VERSION="0.0.1"
while getopts "r:t:v::g" arg; do
  case "${arg}" in
    r)  # Repo
      REPO=${OPTARG}
      ;;
    t)  # Tag
      TAG=${OPTARG}
      ;;
    v)  # Version
      VERSION=${OPTARG}
      ;;
    g)  # Follow GCP Format
      GCP=true
      ;;
    *)
      usage
      ;;
  esac
done
if [ -z "$REPO" ] || [ -z "$TAG" ]; then
  usage
fi

if [ "$GCP" = true ]; then
  if [ -n "$GCP_AR_ID" ] && [ -n "$GCP_PROJECT_ID" ] && [ -n "$GCP_REGION" ]; then
    REPO="${GCP_REGION}/${GCP_PROJECT_ID}/${GCP_AR_ID}"
  else
    echo "Can't build image for GCP -- missing configs:"
    echo "GCP_AR_ID: $GCP_AR_ID"
    echo "GCP_PROJECT_ID: $GCP_PROJECT_ID"
    echo "GCP_REGION: $GCP_REGION"
    exit
  fi
fi

REPOTAG="${REPO}/${TAG}:${VERSION}"

# Create docker repo
if test -d dockerbuild; then
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
    rsync -av "$mod" "api/dockerbuild" --exclude .venv --exclude .idea --copy-links
  fi
  echo "\n"
done
cd api
# Restore arguments
eval "set -- $old"


docker build --tag="${REPOTAG}" .
docker system prune -a --filter "label=stage=intermediate" --force
#
#docker stop servicestest
#docker system prune -a
#docker build . -t servicestest:1.0.2
#docker run -d -p 8081:8081 --name=servicestest servicestest:1.0.2