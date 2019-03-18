#!/bin/bash

action=$1

files="-f kafka-compose.yml -f sim-druid-grafana-compose.yml -f connect-compose.yml -f framework-redis-compose.yml"

if [ $action == 'up' ]
then
  docker-compose ${files} up --build --remove-orphans --detach
elif [ $action == 'down' ]
then
  docker-compose ${files} down --remove-orphans
else
  echo "Unknown action"
  exit 1
fi

