# wp1.3

running the POC on a linux laptop with docker and docker-compose installed.

STEP1 - git clone project

STEP2 -

*** for HPE intranet network only, setup proxy... ***

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

`demo/compose.sh up`

which uses the modular docker-compose files and does

`cd demo &&  docker-compose -f kafka-compose.yml -f connect-compose.yml -f sim-influx-grafana-compose.yml up --build --remove-orphans -d`
