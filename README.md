# wp1.3

In order to run the PoC, some prerequisites have to be fulfilled:

- Use a Linux system
- Install bash
- Install wget
- Install git
- Install Docker Engine (minimal version 18.04)
- Install docker-compose (minimal version 1.23)

STEP1 - git clone project

STEP2 -

*** for HPE intranet network only, setup proxy for the Docker Engine ***

TBD: See https://docs.docker.com/network/proxy/ to improve the proxy support

- `mkdir -p /etc/systemd/system/docker.service.d`
- create a file "/etc/systemd/system/docker.service.d/http-proxy.conf
- cat /etc/systemd/system/docker.service.d/http-proxy.conf

```bash
[Service]
Environment="HTTP_PROXY=http://web-proxy.corp.hpecorp.net:8080" "HTTPS_PROXY=http://web-proxy.corp.hpecorp.net:8080" 

```
- also add a file /etc/docker/daemon.json

```bash
{
  "insecure-registries" : ["o184i024.gre.smktg.hpecorp.net:4567"],
  "dns" : ["16.110.135.51", "8.8.8.8"],
  "dns-search" : ["emea.hpqcorp.net"]
}

```

- `systemctl daemon-reload`
- `systemctl restart docker`

NOTE: If you have another DNS (local e.g.) then add it to the dns list. If you refer to your own DNS as 127.0.0.1, then change it to your own IP address so that it's propagated correctly in the containers you'll be creating.

STEP3

`cd demo`
`./compose.sh up`

Check that the Docker Engine is able to download the Container Images correctly and at the end the following command should look like this:

`docker ps`

```bash
CONTAINER ID        IMAGE                             COMMAND                  CREATED              STATUS              PORTS                                                                                                                                                                                            NAMES
80d886bdf46e        demo_simulator                    "/bin/sh -c 'python …"   About a minute ago   Up About a minute                                                                                                                                                                                                    demo_simulator_1_9a6b22522b2d
a574595a3bfa        grafana/grafana                   "/run.sh"                About a minute ago   Up About a minute   0.0.0.0:3000->3000/tcp                                                                                                                                                                           demo_grafana_1_f528a89706ba
8aacb4186491        demo_framework                    "/usr/local/bin/mvn-…"   About a minute ago   Up About a minute   0.0.0.0:8080->8080/tcp                                                                                                                                                                           demo_framework_1_8ed2f59fa8a8
04cf1daac9a8        demo_kafka-embedded-client-1      "/bin/sh -c '/simul …"   About a minute ago   Up About a minute                                                                                                                                                                                                    demo_kafka-embedded-client-1_1_bcd92305d026
e422c0b4f4fc        demo_druid                        "/bin/sh -c 'bin/sup…"   About a minute ago   Up About a minute   0.0.0.0:1527->1527/tcp, 0.0.0.0:3306->3306/tcp, 0.0.0.0:8200->8200/tcp, 0.0.0.0:9095->9095/tcp, 0.0.0.0:8181->8081/tcp, 0.0.0.0:8182->8082/tcp, 0.0.0.0:8183->8083/tcp, 0.0.0.0:8190->8090/tcp   demo_druid_1_16899f5fe221
ddcf79ac5880        demo_mousttic-1                   "/bin/sh -c 'export …"   About a minute ago   Up About a minute                                                                                                                                                                                                    demo_mousttic-1_1_4f539488f46f
7004732590bb        confluentinc/cp-zookeeper:5.0.0   "/etc/confluent/dock…"   About a minute ago   Up About a minute   2888/tcp, 0.0.0.0:2181->2181/tcp, 3888/tcp                                                                                                                                                       demo_zookeeper_1_c15ceb897905
df8d947c8786        redis:5.0.3                       "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:6379->6379/tcp                                                                                                                                                                           demo_redis_1_27bdf0fbd073
a4eaebd90fca        eclipse-mosquitto:latest          "/docker-entrypoint.…"   About a minute ago   Up About a minute   0.0.0.0:1883->1883/tcp, 0.0.0.0:9001->9001/tcp                                                                                                                                                   demo_mosquitto_1_a74f643e1e61
```

To stop the stack, use the `./compose.sh down` command
