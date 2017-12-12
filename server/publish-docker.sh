#!/bin/bash

# check if we're in the same directory as the dockerfile we need to build
if [ $(basename $(pwd)) != "server" ]; then
  echo "Must be run from 'server' directory"
  exit 1
fi

FORCE="FALSE"
DEV="FALSE"
PROD="FALSE"
VERSION=$(cat version.txt)

for arg in "$@"; do
  case "$arg" in
    "-dev") DEV="TRUE" ;;
    "-prod") PROD="TRUE" ;;
    "-f") FORCE="TRUE" ;;
  esac
done

function buildAndPush {
  REPO=$1
  VERSION=$2
  DOCKERFILE=$3
  FORCE=$4
  # if we receive a 200 status code from docker hub, this version already exists
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://hub.docker.com/v2/repositories/$REPO/tags/$VERSION/)
  if [ $STATUS == "200" ]; then
    if [ $FORCE == "TRUE" ]; then
      echo "Overwriting version $VERSION"
    else
      echo "Tag already exists. Use '-f' to force."
      exit 1
    fi
  else
    if [ $STATUS != "404" ]; then
      echo "Received status code '$STATUS' from Docker Hub."
      exit 1
    fi
  fi

  docker build -t "$REPO:$VERSION" -f "$DOCKERFILE" .
  docker push "$REPO:$VERSION"  
}

if [ $PROD == "TRUE" ]; then
  buildAndPush "pjtatlow/geney-server" $VERSION "docker/prod.dockerfile" $FORCE
fi

if [ $DEV == "TRUE" ]; then
  buildAndPush "pjtatlow/geney-dev-server" $VERSION "docker/dev.dockerfile" $FORCE
fi
