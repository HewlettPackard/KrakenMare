FROM grafana/grafana

USER root
RUN apt update && apt install -y wget

RUN wget https://github.com/Plonk42/druidplugin/archive/ten-sec-granularity.tar.gz \
    && tar zxvpf ten-sec-granularity.tar.gz && mv druidplugin-ten-sec-granularity /var/lib/grafana/plugins/druidplugin \
    && rm ten-sec-granularity.tar.gz
