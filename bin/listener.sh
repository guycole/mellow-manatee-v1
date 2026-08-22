#!/bin/bash
#
# Title: listener.sh
# Description: start the ais listener
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
PYTHONPATH="$HOME/github/mellow-manatee-v1/src"; export PYTHONPATH
#
hostname=$(hostname)
logger -p local3.info "listener manatee $hostname"
#
WORK_DIR="/home/wombat/github/mellow-manatee-v1/src/collector"
#
echo "start listener"
cd $WORK_DIR
source venv/bin/activate
python3 ./listener.py
echo "end listener"
#
