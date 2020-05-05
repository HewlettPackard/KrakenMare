KrakenMare is a containerized software stack providing a versatile data pipeline to monitor HPC clusters.
The source code is provided under the Apache License version 2.0 (See [LICENSE](LICENSE) file at the root of the tree)
The data is provided under the Creative Common 0 License version 1.0 (See [LICENSE.data](LICENSE.data) file at the root of the tree)

# SINGLE MACHINE setup

Configuration: 
- Minimum RAM = 16 GB, Minimum Cores = 4
- Recommended RAM = 32GB, Recommended Cores = 8

Next steps have to be performed as superuser (root)

## Install Docker

Install docker (you may use instructions at https://github.com/bcornec/Labs/tree/master/Docker#docker-installation

Check it works:

`#` **`docker run hello-world`**

**ONLY for proxy-challenged IT departments**

you may need to perform the following tasks:

`#` **`mkdir -p /etc/systemd/system/docker.service.d/`**

`#` **`cat > /etc/systemd/system/docker.service.d/http-proxy.conf << EOF`**
```none
[Service]
Environment="HTTP_PROXY=http://web-proxy.domain.net:8080" "HTTPS_PROXY=http://web-proxy.domain.net:8080" "NO_PROXY=<insert-your-hostname-here>"
EOF
```

Note: change web-proxy.domain.net to the name of your proxy machine and adapt as well the port used.

`#` **`mkdir -p /etc/docker`**

`#` **`echo '{"registry-mirrors": ["http://myregistry:5000"], "insecure-registries": ["http://myregistry:5000", "http://myregistry:5001"], "dns": ["8.8.8.8", "4.4.4.4"]}' > /etc/docker/daemon.json`**

Note: adjust the 8.8.8.8 and 4.4.4.4 IP addresses to match your DNS IP addresses and myregistry to the name of your registry machine. For single machine setup the registry is the current hostname.

`#` **`systemctl daemon-reload`**

`#` **`systemctl restart docker`**

You may want to read https://docs.docker.com/engine/admin/systemd/#http-proxy

**For all IT departments**

## Install docker-compose 1.25.5

`#` **`sudo curl -L https://github.com/docker/compose/releases/download/1.25.5/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose`**

`#` **`chmod +x /usr/local/bin/docker-compose`**

Next steps have to be performed as a docker capable user (able to laucnh docker commands, user belonging to the docker group e.g.)

## Create a km.conf file

`$` **`cp playbooks/km.conf ~/km.conf`**

Note: edit it to match your setup

## Create a swarm cluster

`$` **`docker swarm init --advertise-addr x.y.z.t `**

Note: x.y.z.t is a local IP address to attach to

## Label your local machine with all KM labels

`$` **`for label in broker-1 broker-2 broker-3 fanin registry framework injectors test-tools supervisory_cloud; do docker node update --label-add $label=true `hostname`; done`**

## Setup registries

`$` **`./setup.sh -r`**

Note:  this will start two registry, a mirror registry and a proxy registry

`$` **`docker ps `**
```none
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
df2b2c0bd90f        registry            "/entrypoint.sh /etc..."   5 seconds ago       Up 5 seconds        0.0.0.0:5000->5000/tcp   docker-registry_registry-mirror_1
75a0537d3758        registry            "/entrypoint.sh /etc..."   57 minutes ago      Up 5 seconds        0.0.0.0:5001->5000/tcp   docker-registry_registry-private_1
```

Check that docker ps shows two registries

## Build the stack

`$` **`./setup.sh -b`**
 
This will build the stack from the Internet, can be very long depending on Internet connection

`$` **`./setup.sh -d`**

This will deploy all containers and start the stack
Then run a sanity check... after a while (stack may take up to 5 minutes to start)

`$` **`./setup.sh -s`**
```none
running:timeout 10 mosquitto_sub -h mosquitto -p ok ... see logs </tmp/mosquitto>
running:kafkacat -b broker-1 -L                  ok ... see logs </tmp/broker-1>
running:kafkacat -b broker-2:9093 -L             ok ... see logs </tmp/broker-2>
running:kafkacat -b broker-3:9094 -L             ok ... see logs </tmp/broker-3>
running:redis-cli -h redis ping                  ok ... see logs </tmp/redis>
running:curl -s framework:8080/agents            ok ... see logs </tmp/framework>
running:curl -s http://druid:8081/status/health  ok ... see logs </tmp/druid_coord>
running:curl -s http://druid:8082/status/health  ok ... see logs </tmp/druid_broker>
running:curl -s http://druid:8083/status/health  ok ... see logs </tmp/druid_histo>
running:curl -s http://druid:8090/status/health  ok ... see logs </tmp/druid_overlord>
running:curl -s http://druid:8091/status/health  ok ... see logs </tmp/druid_middle>
running:kafkacat -L -X ssl.ca.location=/run/secr ok ... see logs </tmp/ssl-broker-1>
running:kafkacat -L -X ssl.ca.location=/run/secr ok ... see logs </tmp/ssl-broker-2>
running:kafkacat -L -X ssl.ca.location=/run/secr ok ... see logs </tmp/ssl-broker-3>
running:curl -s http://prometheus:9090/api/v1/ta ok ... see logs </tmp/prometheus>
running:curl -s --cacert /run/secrets/km-ca-1.cr ok ... see logs </tmp/schemaregistry>
running:kafkacat -b broker-1:29092 -L -X securit ok ... see logs </tmp/sasl-broker-1>
running:kafkacat -b broker-2:29093 -L -X securit ok ... see logs </tmp/sasl-broker-2>
running:kafkacat -b broker-3:29094 -L -X securit ok ... see logs </tmp/sasl-broker-3>
running:curl -s --cacert /run/secrets/km-ca-1.cr ok ... see logs </tmp/schemaregistry>
number of messages in KAFKA on the fabric topic... @time = 1587455812 : 320242
```
# Brief description of services as ordered by all-compose.yml
## zookeeper
A single zookeeper using confluent cp-zookeeper image as base is started with security features enabled.
## kafka broker
Three brokers each on their own set of ports with both open 9XXX and SASL authentication/TLS encrypted 2XXX) ones. Each broker has it's own label enabling multi node in swarm.
Sizing of Java memory is controlled by km.conf file created above.
## mosquitto
Eclipse mosquitto broker with security enabled. It is co-located with fanin service.
## test-tools
Multipurpose test container. Used by setup.sh to check pipeline.
## fanin
Reads messages from mqtt and sends to kafka
## druid
Apache druid in single server configuration. Size is controlled by km.conf.
## grafana
Grafana 6.6.2 (needed for support of Druid plugin) configured to read from Druid database and to display Prometheus Kafka metrics.
## schemaregistry
Confluent schemaregistry as central repository of Avro schema
## framework
Agent, device and sensor regisitration server. Uses redis for backend
## redis
Backend for framework
## prometheus
Kafka performance metrics exporter for Grafana
## config-zookeeper
Adds users for services
## config-schemaregistry
Creates Avro schema files from Avro definition files and pushes to schemaregistry
## config-druid
Pushes ingestion spec into druid
## config-kafka
Creates and configures topics
## simulator
Sample agent that automatically runs to show all features
## elastic
Elasticsearch for persisting agent, device, sensor registration data
## config-connect
Configures elasticsearch sink connectors
## connect
Kafka connect for sink to elasticsearch.
## redfish
Sample redfish agent is configured (via RedfishAgent.cfg) to contact HPE's externally available
iLO simulator at https://ilorestfulapiexplorer.ext.hpe.com/redfish/v1 .
Further documentation on iLO REST API can be found at https://www.hpe.com/us/en/servers/restful-api.html 

As this network path may not function we do not start the agent at stack start up.  Please use

`#` **`docker service logs -f krakenmare_redfish`**

until it reports

```none
use: /redfish/start.sh to actually start the container payload.
```

Please enter the container with 

```none
docker exec -ti `docker ps | grep redfish | awk '{print $1}'` bash
```
and run as above or use
```none
docker exec `docker ps | grep redfish | awk '{print $1}'` /redfish/start.sh
```

The agent requests the chassis and from each chassis the temperatures and fans building up a map of sensors.
This process takes several seconds.

The agent registers itself and it's map of sensors and queries the iLO once a minute.
