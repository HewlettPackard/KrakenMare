FROM registry
ENV HTTP_PROXY "http://web-proxy.corp.hpecorp.net:8080/"
ENV HTTPS_PROXY "http://web-proxy.corp.hpecorp.net:8080/"
ENV FTP_PROXY "http://web-proxy.corp.hpecorp.net:8080/"
ENV NO_PROXY "localhost,127.0.0.0/8"
RUN echo -e "proxy:\n remoteurl: https://registry-1.docker.io" >> /etc/docker/registry/config.yml