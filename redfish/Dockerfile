FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y wget gnupg
# Use python-redfish for now
RUN wget http://ftp.project-builder.org/ubuntu/18.04/python-redfish.sources.list -O /etc/apt/sources.list.d/python-redfish.sources.list
# CI is broken for ftp tranfert support and proxy amending...
RUN perl -pi -e 's|ftp://|http://|' /etc/apt/sources.list.d/python-redfish.sources.list
RUN wget -qO - http://ftp.mondorescue.org/ubuntu/18.04/python-redfish.pubkey | apt-key add -
RUN apt-get update -o Acquire::http::No-Cache=True && apt-get install -y python-redfish
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
