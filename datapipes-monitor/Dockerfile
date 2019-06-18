FROM ubuntu:18.04

RUN apt update && apt install -y python3 python3-pip wget
RUN pip3 install --upgrade pip
RUN pip3 install paho-mqtt kafka-python requests pytoml pytz cherrypy influxdb

WORKDIR /workdir
COPY ./www/ /workdir/www/
COPY ./*.py /workdir/
COPY ./*.toml /workdir/
COPY ./*.sh /workdir/

RUN wget https://code.jquery.com/jquery-3.3.1.slim.min.js -P /workdir/www/js
RUN wget https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js -P /workdir/www/js
RUN wget https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css -P /workdir/www/js
RUN wget https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js -P /workdir/www/js
RUN wget https://d3js.org/d3.v5.min.js -P /workdir/www/js
RUN wget https://unpkg.com/sunburst-chart@1.3.1/dist/sunburst-chart.min.js -P /workdir/www/js

WORKDIR /workdir
ENTRYPOINT [ "/bin/bash" ]

CMD ["./datapipe-monitor.sh"]
# To devel/test :
# Put CMD in comment
# Without CMD : build the container, run the container :
# docker build -t datapipes-monitor ./datapipes-monitor/
# docker network ls
# docker run -ti -p7575:7575 --network NAME_OF_DEFAULT_NETWORK --rm datapipes-monitor
# docker run -ti -p7575:7575 --network demo_default --rm datapipes-monitor
