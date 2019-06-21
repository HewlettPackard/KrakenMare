#!/bin/bash

testNB=0
cd /tmp/wp1.3 || exit 1
for ((i=1;i<=10;i++))
do
    if [ "$testNB" != "0" ] ; then
	echo stopping stack test${testNB}
	docker stack rm test${testNB} &> /dev/null
	sleep 60
	#sometimes you need to docker stack rm twice to get rid of the network.
	#one every ten times maybe... do not fatal fail here
	docker stack rm test${testNB} || exit 1 
	sleep 60
    fi
    cd playbooks || exit 1
    testNB=$((testNB+1))
    docker stack deploy -c ../all-compose.yml  -c ../docker-proxy.yml test${testNB} || exit 1
    sleep 480
    docker exec $(docker ps | grep test-t | awk '{ print $1}') /tmp/check-pipeline.sh || exit 1
    cd -
done
