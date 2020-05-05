#!/bin/bash
#
# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#


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

# Under high load, we have seen resident memory of 512MB so setting to 1GB to be safe. Can be set to 256MB for local testing.

/tmp/wait-for --timeout=240 redis:6379 \
    && /tmp/wait-for --timeout=240 broker-1:9092 \
    && /tmp/wait-for --timeout=240 broker-2:9093 \
    && /tmp/wait-for --timeout=240 broker-3:9094 \
    && /tmp/wait-for --timeout=240 mosquitto:8883 \
    && /tmp/wait-for --timeout=240 schemaregistry:8081 -- \
        java -server -Xms${KM_FM_XMS} -Xmx${KM_FM_XMX} \
        -cp target/framework-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
        -XX:+ExitOnOutOfMemoryError -XX:+HeapDumpOnOutOfMemoryError \
        -Djava.util.logging.config.file=/opt/krakenmare/framework/log.properties \
        com.hpe.krakenmare.Main &

sleep infinity
