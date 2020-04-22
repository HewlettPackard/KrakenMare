#!/bin/bash - 

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# -- license --
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
/tmp/wait-for --timeout=240 broker-1:29092 && \
/tmp/wait-for --timeout=240 broker-2:29093 && \
/tmp/wait-for --timeout=240 broker-3:29094 -- /opt/collectd/sbin/collectd -f
