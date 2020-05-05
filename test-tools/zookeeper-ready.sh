#!/bin/bash

#script must be killed or invoked with timeout

while true
do
    #ARE YOU OK 
    echo ruok | nc zookeeper 2181 > /tmp/out-$$
    if [ "$?" == 0 ] ; then
	if grep -q imok /tmp/out-$$ ; then
	    echo zookeeper ready
	    exit 0
	else
	    echo -n "zookeeper not ok but responding..."
	    cat /tmp/out-$$
	    exit 1
	fi
    fi
    sleep 0.3
done

