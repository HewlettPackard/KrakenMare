FROM alpine:edge

RUN apk add python2 py2-pip
RUN pip install paho-mqtt

COPY fake-ibswitchquery.py r1i0c-ibswitch r1i1c-ibswitch /simulator/
COPY seed/* /tmp/

WORKDIR /simulator
ENTRYPOINT python fake-ibswitchquery.py
