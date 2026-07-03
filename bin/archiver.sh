#!/bin/bash
#
# Title: archiver.sh
# Description: tar success directory and save in export
# Development Environment: ubuntu 22.4.5 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
TODAY=$(date '+%Y-%m-%d')
FILE_NAME="manatee-${TODAY}.tgz"
#
EXPORT_DIR="export"
SOURCE_DIR="manatee"
SUCCESS_DIR="success"
WORK_DIR="/var/wombat/fresh"
#
echo "start archiver" 
#
cd ${WORK_DIR}
#
mv ${SUCCESS_DIR} ${SOURCE_DIR}
mkdir ${SUCCESS_DIR}
#
tar -cvzf ${FILE_NAME} ${SOURCE_DIR}
mv ${FILE_NAME} ${EXPORT_DIR}
#
echo "cleanup"
rm -rf ${SOURCE_DIR}
#
echo "end archiver"
#
