#!/bin/bash
#
# Title: docker_build.sh
# Description: build manatee Docker image — Linux hosts only
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
if [ "$(uname -s)" != "Linux" ]; then
    echo "error: this build must run on a Linux host (detected: $(uname -s))"
    exit 1
fi
#
WOMBAT_UID=$(id -u wombat 2>/dev/null)
WOMBAT_GID=$(id -g wombat 2>/dev/null)
#
if [ -z "${WOMBAT_UID}" ] || [ -z "${WOMBAT_GID}" ]; then
    echo "error: wombat user not found on this host"
    exit 1
fi
#
echo "building manatee:latest with WOMBAT_UID=${WOMBAT_UID} WOMBAT_GID=${WOMBAT_GID}"
#
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
#
docker build \
    --build-arg WOMBAT_UID="${WOMBAT_UID}" \
    --build-arg WOMBAT_GID="${WOMBAT_GID}" \
    -t manatee:latest \
    "${SCRIPT_DIR}/src/wombat_docker"
#
echo "done"
#
