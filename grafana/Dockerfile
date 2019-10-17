FROM grafana/grafana

USER root
RUN apk update && apk add wget

ARG commit=67400f89786b476635e0e87cf6ac038a83818672

RUN wget https://github.com/Plonk42/druidplugin/archive/$commit.tar.gz \
    && tar zxvpf $commit.tar.gz && mv druidplugin-$commit /var/lib/grafana/plugins/druidplugin \
    && rm $commit.tar.gz
