#!/bin/bash

host=$1

mvn assembly:assembly -DdescriptorId=jar-with-dependencies

scp target/*-jar-with-dependencies.jar root@${host}:/opt/clmgr/plugins
ssh root@${host} service cmu stop
# ssh root@${host} rm -f /opt/clmgr/log/*
ssh root@${host} service cmu start

exit 0
