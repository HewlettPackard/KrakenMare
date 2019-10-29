#!/bin/sh
# Assemble the individual schema in framework into standalone ones
cp framework/com.hpe.krakenmare.core-sensor.avsc com.hpe.krakenmare.core-agent.avsc
cat framework/com.hpe.krakenmare.core-device.avsc >> com.hpe.krakenmare.core-agent.avsc
cat framework/com.hpe.krakenmare.core-agent.avsc >> com.hpe.krakenmare.core-agent.avsc
sed -i s'/"type": {"type": "string", "logicalType":"uuid"}/"type": ["null", {"type": "string", "logicalType":"uuid"}]/' com.hpe.krakenmare.core-agent.avsc

cp framework/com.hpe.krakenmare.core-sensor.avsc com.hpe.krakenmare.core-device.avsc
cat framework/com.hpe.krakenmare.core-device.avsc >> com.hpe.krakenmare.core-device.avsc
sed -i s'/"type": {"type": "string", "logicalType":"uuid"}/"type": ["null", {"type": "string", "logicalType":"uuid"}]/' com.hpe.krakenmare.core-device.avsc

cp framework/com.hpe.krakenmare.core-sensor.avsc com.hpe.krakenmare.message.agent-device.list.avsc
cat framework/com.hpe.krakenmare.core-device.avsc >> com.hpe.krakenmare.message.agent-device.list.avsc
cat framework/com.hpe.krakenmare.message.agent-device.list.avsc >> com.hpe.krakenmare.message.agent-device.list.avsc
sed -i s'/"type": {"type": "string", "logicalType":"uuid"}/"type": ["null", {"type": "string", "logicalType":"uuid"}]/' com.hpe.krakenmare.message.agent-device.list.avsc
