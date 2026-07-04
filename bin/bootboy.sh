#!/bin/bash
#
# Title: bootboy.sh
# Description: configure 
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
hostname=$(hostname)
logger -p local3.info "bootboy manatee $hostname"
#
WORK_DIR="/home/wombat/github/mellow-manatee-v1/src/collector"
#
echo "start bootboy"
cd $WORK_DIR
source venv/bin/activate
python3 ./bootboy.py
echo "end bootboy"
#
