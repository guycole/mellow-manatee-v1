#!/bin/bash
#
# Title: wombat-pull.sh
# Description: Pull the latest wombat docker image
# Development Environment: ubuntu 22.4.5 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
REGISTRY="ghcr.io"
OWNER="guycole"
IMAGE="wombat-manatee"
TAG="latest"
#
echo "pulling ${REGISTRY}/${OWNER}/${IMAGE}:${TAG}"
docker pull "${REGISTRY}/${OWNER}/${IMAGE}:${TAG}"
#
echo "done"
#
