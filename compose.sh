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
	dever=`docker --version`
	demaj=`echo $dever | cut -d' ' -f3 | cut -d'.' -f1`
	demin=`echo $dever | cut -d' ' -f3 | cut -d'.' -f2`
	if [ $demaj -lt 17 ]; then
		echo "Minimal supported docker engine is 17.09 (found $demaj)"
		exit -1
	elif [ $demaj -eq 17 ] && [ $demin -lt 9 ]; then
		echo "Minimal supported docker engine is 17.09 (found $demaj.$demin)"
		exit -1
	else
		echo "Using $dever"
	fi

	dcver=`docker-compose --version`
	dcmaj=`echo $dcver | cut -d' ' -f3 | cut -d'.' -f1`
	dcmin=`echo $dcver | cut -d' ' -f3 | cut -d'.' -f2`
	if [ $dcmaj -lt 1 ]; then
		echo "Minimal supported docker-compose is 1.17 (found $dcmaj)"
		exit -1
	elif [ $dcmaj -eq 1 ] && [ $dcmin -lt 17 ]; then
		echo "Minimal supported docker-compose is 1.17 (found $dcmaj.$dcmin)"
		exit -1
	else
		echo "Using $dcver"
	fi

	docker-compose up --build --remove-orphans -d
elif [ "$action" == "down" ]; then
	docker-compose down --remove-orphans
else
	echo "Unknown action"
	exit 1
fi
