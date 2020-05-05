#!/bin/bash

/tmp/wait-for --timeout=240 connect:8083 || exit 1

# configure the elastic connector
until curl -s https://connect:8083/ --cert /run/secrets/connect.certificate.pem --key /run/secrets/connect.key  --cacert /run/secrets/km-ca-1.crt; do
  sleep 1
done

/tmp/configure-connect.sh
