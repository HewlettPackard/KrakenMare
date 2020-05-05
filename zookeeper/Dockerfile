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

FROM  confluentinc/cp-zookeeper:5.4.0

# requirement for wait-for and change to Java 11
RUN apt-get update && apt-get install -y netcat wget sed zulu-11 && apt-get remove -y zulu-8 
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -                  
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# JMX Prometheus exporter
RUN mkdir /opt/prometheus &&\
    wget https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.12.0/jmx_prometheus_javaagent-0.12.0.jar -P /opt/prometheus &&\
    wget https://github.com/prometheus/jmx_exporter/raw/master/example_configs/kafka-2_0_0.yml -P /opt/prometheus

CMD ["/etc/confluent/docker/run"]

