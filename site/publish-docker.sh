#!/bin/bash

# check if we're in the same directory as the dockerfile we need to build
if [ $(basename $(pwd)) != "site" ]; then
  echo "Must be run from 'site' directory"
  exit 1
fi

FORCE="FALSE"
REPO="pjtatlow/geney-ui"
VERSION=$(cat version.txt)

# parse command line arguments to check for a -f
while getopts ":f" opt; do
  case $opt in
    f)
      FORCE="TRUE"
      ;;
  esac
done

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

npm run build
docker build -t "$REPO:$VERSION" .
docker push "$REPO:$VERSION"
