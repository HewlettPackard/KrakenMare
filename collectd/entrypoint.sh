#!/bin/bash - 
#===============================================================================
#
#          FILE: entrypoint.sh
# 
#         USAGE: ./entrypoint.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Jeff Hanson (), jeff.hanson@hpe.com
#  ORGANIZATION: ATG
#       CREATED: 05/30/2019 08:42:40 AM
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error
cd /opt/collectd/etc
sed -i "s/Key \"localhost\"/Key \"$HOSTNAME\"/" collectd.conf
grep "Key \"" collectd.conf
export LD_LIBRARY_PATH=/usr/local/lib
/opt/collectd/sbin/collectd -f
