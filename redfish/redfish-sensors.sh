#!/bin/bash

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
	COMMAND="/bin/bash"
fi
if [ "$COMMAND" != "/bin/bash" ]; then 
	echo "Run redfish-sensors.py"
	/redfish-sensors.py
	sleep infinity
else
	$COMMAND
fi
