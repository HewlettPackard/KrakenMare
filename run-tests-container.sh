#!/bin/bash

if [ $# -eq 0 ]; then
	command=""
else
	command=$@
fi

docker run -ti --network demo_default --rm demo_test-tools $command

