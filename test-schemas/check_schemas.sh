#!/bin/bash

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
while [ "$c" -eq "-1" ];
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

#as long as number of schemas is 0 loop...
while [ "$c" == "0" ];
do
    sleep 10
    c=$(count)
done

#now that it is not zero, just wait it stabilizes value for 10 seconds
while : ; do
    cprev=$c
    sleep 20
    c=$(count)
    [[ "$c" != "$cprev" ]] || break
done

echo "$c schemas so far"

exit 0



