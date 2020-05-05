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

# Wait for required services to be up
/tmp/wait-for --timeout=240 mosquitto:8883 || exit 1
/tmp/wait-for --timeout=240 framework:8080 || exit 1
/tmp/wait-for --timeout=240 schemaregistry:8081 || exit 1
/simulator/check_schemas.sh || exit 1

cd /simulator

python3 IBswitchSimulator.py --encrypt --batching --numberOfTopic=2 --sleepLoopTime=0.01 --enableMQTTbatchesCounter
#--debug --encrypt --batching --numberOfTopic=2 --sleepLoopTime=0 --enableMQTTbatchesCounter
sleep infinity

