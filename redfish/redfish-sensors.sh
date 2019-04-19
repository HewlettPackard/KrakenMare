#!/bin/bash

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
	redfish-client config add dl560g10 https://$REDFISHIP/redfish/v1 "$REDFISHACC" "$REDFISHPWD"
	python2 /redfish-sensors.py
else
	$COMMAND
fi
