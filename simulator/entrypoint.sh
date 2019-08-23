#!/bin/bash

# Wait for all three brokers to be up
/tmp/wait-for --timeout=240 broker-1:9092 || exit 1
/tmp/wait-for --timeout=240 broker-2:9093 || exit 1
/tmp/wait-for --timeout=240 broker-3:9094 || exit 1

cd /simulator
python3 IBswitchSimulator.py --mode=kafka
