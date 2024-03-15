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

FROM confluentinc/cp-enterprise-kafka:5.4.0
#FROM confluentinc/cp-server:5.4.1-1-deb8
#A requirement for wait-for
RUN apt-get --allow-unauthenticated install -y sed
RUN sed -i 's/\/debian\./\/archive\.debian\./g' /etc/apt/sources.list
RUN sed -i 's/deb http:\/\/security/#deb http:\/\/security/g' /etc/apt/sources.list
RUN  apt-get --allow-unauthenticated update
RUN  apt-get --allow-unauthenticated install -y netcat wget sed zulu-11 && apt-get remove -y zulu-8 
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -                  
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# JMX Prometheus exporter
RUN mkdir /opt/prometheus &&\
    wget https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.12.0/jmx_prometheus_javaagent-0.12.0.jar -P /opt/prometheus &&\
    wget https://raw.githubusercontent.com/prometheus/jmx_exporter/main/example_configs/kafka-2_0_0.yml -P /opt/prometheus

COPY kafka-broker/entrypoint.sh test-tools/zookeeper-ready.sh /etc/confluent/docker/

CMD ["/etc/confluent/docker/entrypoint.sh"]
