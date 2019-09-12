#!/bin/bash

/tmp/wait-for --timeout=240 schemaregistry:8081 || exit 1

cd /tmp
for schema in *.avsc
do
  topic=$(echo $schema | awk -F "." '{$NF=""; print $0}' | sed "s/ /-/g" | sed 's/.$//')
  python3 /tmp/register_schema.py https://schemaregistry:8081 $topic $schema 
done
