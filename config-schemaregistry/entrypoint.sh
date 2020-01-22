#!/bin/bash

/tmp/wait-for --timeout=240 schemaregistry:8081 || exit 1

cd /tmp
for protocol in *.avdl
do
  java -jar avro-tools-1.9.1.jar idl2schemata $protocol
done

for schema in *.avsc
do
  namespace=`jq -r .namespace < $schema`
  # name=`jq -r .name < $schema | tr '[:upper:]' '[:lower:]'`
  name=`jq -r .name < $schema`
  topic=`echo $namespace.$name`
  if ! java -jar avro-cli-0.2.7.jar validate -s $schema > /dev/null 2>&1 ; then
    echo "$schema fails to validate. Not pushed to schema registry. See below" >&2
    java -jar avro-cli-0.2.7.jar validate -s $schema 
  else
    if ! python3 /tmp/register_schema.py https://schemaregistry:8081 $topic $schema ; then
      echo "$schema failed to push to schema registry" >&2
    fi
  fi
done
