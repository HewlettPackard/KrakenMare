#!/bin/bash

/tmp/wait-for --timeout=240 broker-1:9092 && \
/tmp/wait-for --timeout=240 broker-2:9092 && \
/tmp/wait-for --timeout=240 broker-3:9092 && \
/tmp/wait-for --timeout=240 zookeeper:2181 -- bin/supervise -c quickstart/tutorial/conf/quickstart-no-zk.conf
