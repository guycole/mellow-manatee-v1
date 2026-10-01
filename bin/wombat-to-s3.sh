#!/bin/bash 
#
# Title: wombat-to-s3.sh
# Description: move mastodon files from local file system to s3
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin:/opt/homebrew/bin/aws; export PATH
#
DEST_BUCKET=s3://mellow-manatee-uw2-f4343.braingang.net/fresh/
#
# host name is also AWS profile name
HOST_NAME=$(hostname)
#
EXPORT_DIR="export"
WORK_DIR="/var/wombat/manatee"
#
# echo "start s3 move"
cd ${WORK_DIR}/${EXPORT_DIR}
#
if aws s3 mv . "$DEST_BUCKET" --recursive --profile="$HOST_NAME"; then
        : # files removed by s3 mv
else
        echo "s3 mv failed" >&2
        exit 1
fi
#
echo "end s3 transfer"
#
