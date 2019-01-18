FROM alpine:edge

ENV http_proxy http://web-proxy.corp.hpecorp.net:8080
ENV https_proxy http://web-proxy.corp.hpecorp.net:8080

RUN apk add python mosquitto-clients

COPY fake-ibswitchquery.py r1i0c-ibswitch r1i1c-ibswitch /simulator/
COPY seed/* /tmp/

WORKDIR /simulator
ENTRYPOINT python fake-ibswitchquery.py
