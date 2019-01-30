# wp1.3

running the POC on a linux laptop with docker and docker-compose installed.

STEP1 - git clone project
STEP2 -

*** for HPE intranet network only, setup proxy... ***

- mkdir -p /etc/systemd/system/docker.service.d
- create a file "/etc/systemd/system/docker.service.d/http-proxy.conf
- cat /etc/systemd/system/docker.service.d/http-proxy.conf

[Service]
Environment="HTTP_PROXY=http://web-proxy.corp.hpecorp.net:8080" "HTTPS_PROXY=http://web-proxy.corp.hpecorp.net:8080" 

- also add a file /etc/docker/daemon.json

{
  "insecure-registries" : ["o184i024.gre.smktg.hpecorp.net:4567"],
  "dns" : ["16.110.135.51", "8.8.8.8"],
  "dns-search" : ["emea.hpqcorp.net"]
}

- systemctl daemon-reload
- systemctl restart docker

STEP3

cd demo && docker-compose up --build --remove-orphans -d