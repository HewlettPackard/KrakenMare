#!/bin/bash

action=$1
shift
services=$@
nb_services=$#

export COMPOSE_PROJECT_NAME=demo

export COMPOSE_FILE=all-compose.yml:secrets-compose.yml
# Hardcoded for now
export REDFISHIP=${REDFISHIP:-16.19.180.65}
export REDFISHACC=${REDFISHACC:-cmu}
export REDFISHPWD=${REDFISHPWD:-HPinvent}

if [ "$action" == "up" ]; then
	echo "Checking whether we are on the HPE LAN and needing a proxy..."
	if [ ! -x /usr/bin/wget ]; then
	    echo "Unable to find wget in your env, install it to have automatic HPE proxy detection"
	    exit 1
	else
	    wget --no-proxy -q --dns-timeout=2 --timeout=2 www.google.com -O /dev/null
	    if [ ! $? -eq 0 ]; then
		wget -q --dns-timeout=5 --timeout=5 autocache.hpecorp.net -O /dev/null
		if [ $? -eq 0 ]; then
			export COMPOSE_FILE=${COMPOSE_FILE}:docker-proxy.yml
			echo "HPE proxy USED..."
		else
		    echo "network connectivity issue..."
		    exit 1
		fi
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
	cd km-security || exit 1
	#if secret files already exist, use them, if not generate them
	./km-secrets-tool.sh -cg || exit 1
	cd .. || exit 1
	if [ $nb_services -eq 0 ]; then
		echo "Starting all services"
	else
		echo "Starting $nb_services services: $services"
	fi
  case "$(docker info --format '{{.Swarm.LocalNodeState}}')" in
  inactive)
    docker swarm init || exit 1
    ;;
  pending)
    echo "Docker swarm init will fail. Compose is not able to proceed"
    exit 1
    ;;
  active)
    if [ "$(docker info --format '{{.Swarm.ControlAvailable}}')" == "true" ]; then
      echo "Use existing swarm."
    else
      echo "Not on swarm manager. Compose is not able to proceed"
      exit 1
    fi
    ;;
  locked)
    echo "Node is in a locked swarm cluster. Compose is not able to proceed"
    exit 1
    ;;
  error)
    echo "Node is in an error state. Compose is not able to proceed"
    exit 1
    ;;
  *)
    echo "Unknown state $(docker info --format '{{.Swarm.LocalNodeState}}'). Compose is not able to proceed"
    exit 1
  esac
	docker-compose up --build --remove-orphans -d $services
elif [ "$action" == "down" ]; then
	docker-compose down --remove-orphans
else
	echo "Unknown action"
	exit 1
fi

