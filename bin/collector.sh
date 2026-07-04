#!/bin/bash
#
# Title: collector.sh
# Description: drive the collection pass
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
hostname=$(hostname)
logger -p local3.info "collector manatee $hostname"
#
WORK_DIR="/home/wombat/github/mellow-manatee-v1/src/collector"
#
echo "start collector"
sleep 13
cd $WORK_DIR
source venv/bin/activate
python3 ./collector.py
echo "end collector"
#
