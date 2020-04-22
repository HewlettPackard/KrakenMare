#!/bin/bash
	COMMAND="/bin/bash"
if [ "$COMMAND" != "/bin/bash" ]; then 

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

# Wait for all three brokers to be up
/tmp/wait-for --timeout=240 mosquitto:1883 || exit 1
/tmp/wait-for --timeout=240 framework:8080 || exit 1
/tmp/wait-for --timeout=240 schemaregistry:8081 || exit 1

# Hardcoded for now if not defined
export REDFISHIP=${REDFISHIP:="https://16.19.180.65/redfish/v1"}
export REDFISHACC=${REDFISHACC:="cmu"}
export REDFISHPWD=${REDFISHPWD:="HPinvent"}

# Reset values for HPE simulator
if [ "$REDFISHIP" = "https://ilorestfulapiexplorer.ext.hpe.com/redfish/v1" ]; then
	export REDFISHACC=""
	export REDFISHPWD=""
fi

# Useless when harcoding values but keeping for now
COMMAND="/bin/true"
if [ "x$REDFISHIP" = "x" ]; then 
	echo "REDFISHIP not provided - will run bash"
fi
	echo "Run hello-world.py"
	/hello-world.py
	#sleep infinity
else
	$COMMAND
fi
