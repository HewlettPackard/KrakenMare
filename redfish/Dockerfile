FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y wget gnupg apt-utils python-pip perl-modules
# Use python-redfish for now
RUN wget http://ftp.project-builder.org/ubuntu/18.04/python-redfish.sources.list -O /etc/apt/sources.list.d/python-redfish.sources.list
# CI is broken for ftp tranfert support and proxy amending...
RUN perl -pi -e 's|ftp://|http://|' /etc/apt/sources.list.d/python-redfish.sources.list
RUN wget -qO - http://ftp.mondorescue.org/ubuntu/18.04/python-redfish.pubkey | apt-key add -
RUN apt-get update -o Acquire::http::No-Cache=True && DEBIAN_FRONTEND=noninteractive apt-get install -y python-redfish
RUN pip install kafka-python
RUN apt-get update && apt-get install -y netcat 
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/
COPY redfish-sensors.py /
COPY redfish-sensors.sh /
# Point to the test system
ARG REDFISHIP
ARG REDFISHACC
ARG REDFISHPWD
ENV REDFISHIP=$REDFISHIP
ENV REDFISHACC=$REDFISHACC
ENV REDFISHPWD=$REDFISHPWD
RUN echo "Redfish IP: $REDFISHIP"
CMD /redfish-sensors.sh
#CMD sleep infinity
