#!/bin/bash
docker build --tag registry-mirroring . || exit 1
docker run --env REGISTRY_HTTP_ADDR=0.0.0.0:5000 --detach --publish 5000:5000 registry-mirroring || exit 1
