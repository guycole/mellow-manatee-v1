#!/bin/bash 
#
# Title: archiver.sh
# Description: tar success directory and save in archive
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin:/opt/homebrew/bin/aws; export PATH
#
HOST_NAME=$(hostname)
TODAY=$(date '+%Y-%m-%d')
FILE_NAME="${HOST_NAME}-${TODAY}.tgz"
#
ARCHIVE_DIR="archive"
EXPORT_DIR="export"
PEAKER_DIR="peaker"
SOURCE_DIR="manatee-v1"
SUCCESS_DIR="success"
WORK_DIR="/var/wombat/manatee"
#
echo "start archiver"
#
cd ${WORK_DIR}
#
mv ${SUCCESS_DIR} ${SOURCE_DIR}
mkdir ${SUCCESS_DIR}
#
# archive everything
tar -cvzf "${ARCHIVE_DIR}/${FILE_NAME}" ${SOURCE_DIR}
#
# export only json files
tar -cvzf "${EXPORT_DIR}/${FILE_NAME}" ${SOURCE_DIR}/*.json
#
echo "cleanup"
rm -rf ${SOURCE_DIR}
#
echo "end archive"
#