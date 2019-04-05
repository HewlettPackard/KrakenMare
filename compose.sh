#!/bin/bash

action=$1

export COMPOSE_PROJECT_NAME=demo
export COMPOSE_FILE=kafka-compose.yml:sim-druid-grafana-compose.yml:connect-compose.yml:framework-redis-compose.yml

if [ "$action" == "up" ]; then
	echo "Checking whether we are on the HPE LAN and needing a proxy..."
	if [ ! -x /usr/bin/wget ]; then
		echo "Unable to find wget in your env, install it to have automatic HPE proxy detection"
	else
		wget -q --dns-timeout=2 autocache.hpecorp.net -O /dev/null
		if [ $? -eq 0 ]; then
			export COMPOSE_FILE=${COMPOSE_FILE}:docker-proxy.yml
			echo "HPE proxies set up"
		fi
	fi

	docker-compose up --build --remove-orphans -d
elif [ "$action" == "down" ]; then
	docker-compose down --remove-orphans
else
	echo "Unknown action"
	exit 1
fi

