#!/bin/bash
#
# Title: archiver.sh
# Description: tar success directory and save in export
# Development Environment: ubuntu 22.4.5 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
HOST_NAME=$(hostname)
TODAY=$(date '+%Y-%m-%d')
FILE_NAME="${HOST_NAME}-${TODAY}.tgz"
#
ARCHIVE_DIR="archive"
EXPORT_DIR="export"
SOURCE_DIR="manatee-v1"
SUCCESS_DIR="success"
WORK_DIR="/var/wombat/manatee"
#
echo "start archiver" 
#
cd ${WORK_DIR}
#
mv "${WORK_DIR}/${SUCCESS_DIR}" "${WORK_DIR}/${SOURCE_DIR}"
mkdir "${WORK_DIR}/${SUCCESS_DIR}"
#
# archive everything
tar -cvzf "${ARCHIVE_DIR}/${FILE_NAME}" ${SOURCE_DIR}
#
# export only collector files
rm -f "${WORK_DIR}/${SOURCE_DIR}"/manatee*
tar -cvzf "${WORK_DIR}/${EXPORT_DIR}/${FILE_NAME}" ${SOURCE_DIR}
#
echo "cleanup"
rm -rf ${SOURCE_DIR}
#
echo "end archiver"
#
