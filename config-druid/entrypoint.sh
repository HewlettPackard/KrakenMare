#!/bin/bash

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# -- license --

/tmp/wait-for --timeout=240 druid:8081 || exit 1

# wait for supervisor rest API to be up
until curl -s druid:8081/druid/indexer/v1/supervisor; do
  sleep 1
done

echo "Load the indexer for simulator data"
curl -s -XPOST -H'Content-Type: application/json' -d @/tmp/perfquery-index.json http://druid:8081/druid/indexer/v1/supervisor || exit 1
curl -s druid:8081/druid/indexer/v1/supervisor | jq .
echo " Load the indexer for collectd data"
curl -s -XPOST -H'Content-Type: application/json' -d @/tmp/collectd-index.json http://druid:8081/druid/indexer/v1/supervisor || exit 1
curl -s druid:8081/druid/indexer/v1/supervisor | jq .
