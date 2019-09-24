#!/bin/bash
#
# Prints contents of schema registry
#

curl -s --cacert /run/secrets/km-ca-1.crt --cert /run/secrets/schemaregistry.certificate.pem --key /run/secrets/schemaregistry.key -X GET https://schemaregistry:8081/subjects/ | jq .
