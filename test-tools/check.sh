#!/bin/bash
container=`docker ps | grep test-tools | awk '{print $1}'` || exit 1
docker exec -ti $container /tmp/check-pipeline.sh
docker exec -ti $container /tmp/km-scaling-test-rate.sh
