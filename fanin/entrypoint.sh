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

echo "hello from fanin... starting waiting for services..."

# Wait for all three brokers to be up
/tmp/wait-for --timeout=240 mosquitto:8883 || { echo "timeout on mosquitto" ; exit 1 ;  }
/tmp/wait-for --timeout=240 framework:8080 || { echo "timeout on FM" ; exit 1 ;  }
/tmp/wait-for --timeout=240 broker-1:9092 ||  { echo "timeout on b1" ; exit 1 ;  }
/tmp/wait-for --timeout=240 broker-2:9093 ||  { echo "timeout on b2" ; exit 1 ;  }
/tmp/wait-for --timeout=240 broker-3:9094 ||  { echo "timeout on b3" ; exit 1 ;  }
/tmp/wait-for --timeout=240 schemaregistry:8081 || { echo "timeout on schemaregistry" ; exit 1 ;  }
/fanin/check_schemas.sh || exit 1

cd /fanin
# setting the --enableMQTTbatchesCounter will print ATTENTION warnings if some
# messages are lost. This only works when using and exclusively using the IBswitch simulator
# injectors
threads=2
taskset -c 0-$(($threads-1)) python3.7 FanIn.py --encrypt --batching --numberOfTopic=$threads
# python3.7 FanIn.py --encrypt --batching --numberOfTopic=2 --enableMQTTbatchesCounter
#--debug --encrypt --batching --numberOfTopic=2 --enableMQTTbatchesCounter --enableMQTTbatchPassthrough 
sleep infinity
