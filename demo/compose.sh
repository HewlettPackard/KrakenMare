#!/bin/bash

action=$1

files="-f kafka-compose.yml -f sim-druid-grafana-compose.yml -f connect-compose.yml -f framework-redis-compose.yml"

if [ "$action" == "up" ]; then
	echo "Checking whether we are on the HPE LAN and needing a proxy..."
	if [ ! -x /usr/bin/wget ]; then 
		echo "Unable to find wget in your env, intsall it to have automatic HPE proxy detection"
	else
		wget -q --dns-timeout=2 autocache.hpecorp.net -O /dev/null
		if [ $? -eq 0 ]; then
			files="${files} -f docker-proxy.yml"
			echo "HPE proxies set up"
		fi
	fi

	docker-compose ${files} up --build --remove-orphans -d
elif [ "$action" == "down" ]; then
    docker-compose ${files} down --remove-orphans
else
	 echo "Unknown action"
	 exit 1
fi

