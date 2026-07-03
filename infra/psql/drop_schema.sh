#!/bin/bash
#
# Title:drop_schema.sh
# Description: remove schema
# Development Environment: OS X 10.15.2/postgres 12.12
# Author: G.S. Cole (guy at shastrax dot com)
#
export PGDATABASE=manatee
export PGHOST=localhost
export PGPASSWORD=woofwoof
export PGUSER=manatee_admin
#
psql $PGDATABASE -c "drop table manatee_load_log"
#
