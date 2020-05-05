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

RUN apt-get update && apt-get upgrade -y
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y wget gnupg apt-utils python3-pip perl-modules netcat

# Wait
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# Use python-redfish for now
RUN wget http://ftp.project-builder.org/ubuntu/18.04/python-redfish.sources.list -O /etc/apt/sources.list.d/python-redfish.sources.list

# CI is broken for ftp tranfert support and proxy amending...
RUN perl -pi -e 's|ftp://|http://|' /etc/apt/sources.list.d/python-redfish.sources.list
RUN wget -qO - http://ftp.mondorescue.org/ubuntu/18.04/python-redfish.pubkey | apt-key add -
RUN apt-get update -o Acquire::http::No-Cache=True && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-redfish
RUN pip3 install paho-mqtt configparser python-schema-registry-client faust

COPY ./redfish/RedfishAgent.py ./redfish/RedfishAgent.cfg ./redfish/entrypoint.sh ./redfish/version.py ./redfish/start.sh /redfish/

COPY ./redfish/SensorDescriptor/*.json  /redfish/
COPY ./redfish/start.sh /redfish
COPY ./agent-python-module/agentcommon.py /redfish/

WORKDIR /redfish
ENV PYTHONUNBUFFERED=1

CMD ["/redfish/entrypoint.sh"]
