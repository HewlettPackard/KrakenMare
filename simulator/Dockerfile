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

FROM ubuntu:18.04

RUN apt-get update && apt-get install -y netcat wget
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

RUN apt update && apt install -y python3 python3-pip curl jq
RUN pip3 install paho-mqtt configparser python-schema-registry-client faust

# this is image MUST be built from the upper directory (docker build -f simulator/Dockerfile .) to access agentcommon.py

COPY ./simulator/IBswitchSimulator.py ./simulator/version.py ./simulator/IBswitchSimulator.cfg ./simulator/r1i0c-ibswitch ./simulator/r1i1c-ibswitch ./simulator/entrypoint.sh /simulator/
COPY ./agent-python-module/agentcommon.py /simulator/
COPY ./simulator/seed/* /tmp/
COPY ./simulator/SensorDescriptors/*.json /simulator/
COPY ./test-schemas/check_schemas.sh /simulator/

WORKDIR /simulator
ENV PYTHONUNBUFFERED=1

CMD ["/simulator/entrypoint.sh"]
