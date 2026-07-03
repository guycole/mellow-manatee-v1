#!/bin/bash
#
# Title:add_schema.sh
# Description:
# Development Environment: OS X 10.15.2/postgres 12.12
# Author: G.S. Cole (guy at shastrax dot com)
#
# psql -U heeler_py -d heeler
#
export PGDATABASE=manatee
export PGHOST=localhost
export PGPASSWORD=woofwoof
export PGUSER=manatee_admin
#
psql < load_log.psql
#
