#!/bin/bash

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# -- license --

function count () {
    n0=`curl -s --cacert /run/secrets/km-ca-1.crt --cert /run/secrets/schemaregistry.certificate.pem --key /run/secrets/schemaregistry.key -X GET https://schemaregistry:8081/subjects/ | jq . | grep -c com`
    if [ $? -eq 0 ] ; then
	echo $n0
    else
	echo -1
    fi
}

#access the schemaregistry a first time
c=$(count)

try=0
while [ "$c" == "-1" ];
do
    echo "initial access to schemaregistry failed, retrying in 10 secs..."
    sleep 10
    c=$(count)
    try=$((try+1))
    #timeout = 240 seconds 
    if [ "$try" -gt 24 ] ; then
	echo "fatal: last tentative to access schemaregistry failed"
	exit 1
    fi
done

#now that it is not zero, just wait it stabilizes value for 10 seconds
while : ; do
    cprev=$c
    sleep 10
    c=$(count)
    [[ "$c" != "$cprev" ]] || break
done

echo "$c schemas so far"

exit 0



