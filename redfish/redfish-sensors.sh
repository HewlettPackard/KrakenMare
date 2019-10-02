#!/bin/bash

# Wait for all three brokers to be up
/tmp/wait-for --timeout=240 broker-1:9092 || exit 1
/tmp/wait-for --timeout=240 broker-2:9093 || exit 1
/tmp/wait-for --timeout=240 broker-3:9094 || exit 1

env
COMMAND="/bin/true"
if [ "x$REDFISHIP" = "x" ]; then 
	echo "REDFISHIP not provided - will run bash"
	COMMAND="/bin/bash"
fi
if [ "x$REDFISHACC" = "x" ]; then 
	echo "REDFISHACC not provided - will run bash"
	COMMAND="/bin/bash"
fi
if [ "x$REDFISHPWD" = "x" ]; then 
	echo "REDFISHPWD not provided - will run bash"
	COMMAND="/bin/bash"
fi
if [ "$COMMAND" != "/bin/bash" ]; then 
	echo "Run redfish-client"
	redfish-client config add dl560g10 https://$REDFISHIP/redfish/v1 "$REDFISHACC" "$REDFISHPWD"
	echo "Run redfish-sensors.py"
	python2 /redfish-sensors.py
else
	$COMMAND
fi
