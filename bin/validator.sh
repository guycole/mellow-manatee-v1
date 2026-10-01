#!/bin/bash
#
# Title: validator.sh
# Description: verify collection files and write stats
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
set -euo pipefail

PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
IMAGE="${IMAGE:-ghcr.io/guycole/wombat-manatee:latest}"
PULL_IMAGE="${PULL_IMAGE:-0}"

echo "start validate"
echo "host arch: $(uname -m)"
echo "image: ${IMAGE}"
#
if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
	echo "local image missing, pulling ${IMAGE}"
	docker pull "${IMAGE}"
elif [ "${PULL_IMAGE}" = "1" ]; then
	echo "pull requested, updating ${IMAGE}"
	docker pull "${IMAGE}"
fi

docker image inspect --format 'image id: {{.Id}} arch: {{.Architecture}}/{{.Os}}' "${IMAGE}"

docker rm -f manatee-validate >/dev/null 2>&1
docker run -v /var/wombat:/mnt/wombat --name manatee-validate --entrypoint python "${IMAGE}" manatee_app.py
#
#docker rm -f manatee-koala >/dev/null 2>&1
#docker run -e stuntbox=koala -v /var/wombat:/mnt/wombat --name manatee-koala --entrypoint python "${IMAGE}" manatee_app.py
#
#$HOME/github/mellow-manatee-v1/bin/manatee-koala-import.sh
#
echo "end validate"
#
