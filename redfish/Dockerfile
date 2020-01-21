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
RUN pip3 install paho-mqtt configparser python-schema-registry-client

COPY RedfishAgent.py RedfishAgent.cfg entrypoint.sh version.py KrakenMareTriplet.py /redfish/

COPY SensorDescriptor/*.json  /redfish/
COPY start.sh /redfish

WORKDIR /redfish
ENV PYTHONUNBUFFERED=1

CMD ["/redfish/entrypoint.sh"]
