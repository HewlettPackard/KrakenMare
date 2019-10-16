#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Licensed under the APache v2 license
# Copyright Hewlett-Packard Enterprise, 2019

import os
import sys
import io
import time
import json
from datetime import datetime
#from kafka import KafkaProducer
#from kafka.errors import KafkaUnavailableError
import subprocess
import paho.mqtt.client as mqtt
from fastavro import schemaless_writer, schemaless_reader
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import MessageSerializer
import redfish
import uuid
import hashlib

# Time to wait between requests
SLEEP = 120

conf = {
   "url": "https://schemaregistry:8081",
   "ssl.ca.location": "/run/secrets/km-ca-1.crt",
   "ssl.certificate.location":
   "/run/secrets/schemaregistry.certificate.pem",
   "ssl.key.location": "/run/secrets/schemaregistry.key",
}

client = SchemaRegistryClient(conf)
subject = "com-hpe-krakenmare-message-agent-send-time-series"
cg = None

while cg is None:
    cg = client.get_schema(subject)
    print("getting schema %s from schemaregistry" % subject)
    time.sleep(1)

# Hardcoded for now
mqtt_broker = "mosquitto"
mqtt_port = 1883
# Faked UUID
mqttuuid = "a8098c1a-f86e-11da-bd1a-00112444be1e"
machine = str(os.environ['REDFISHIP'])
topic = "redfish/" + machine.split("://")[1].split("/")[0] + '/'
mqttclient = mqtt.Client(mqttuuid)
print("connecting to mqtt broker")
mqttclient.connect(mqtt_broker, mqtt_port)

# Infinite loop
i = 0
while True:
    i = i + 1
    if os.environ['REDFISHACC'] == "":
        simulator = True
        enforceSSL = False
    else:
        simulator = False
        enforceSSL = True
    try:
        redfish_data = redfish.connect(os.environ['REDFISHIP'],
                                    os.environ['REDFISHACC'],
                                    os.environ['REDFISHPWD'],
                                    verify_cert=False,
                                    simulator=simulator,
                                    enforceSSL=enforceSSL)
    except redfish.exception.RedfishException as e:
            sys.stderr.write(str(e.message))
            sys.stderr.write(str(e.advices))
            print("Sleeping " + str(SLEEP) + " seconds")
            time.sleep(SLEEP)
            continue

    # Write the json data to mqtt broker
    measurementList = []
    for chassis in redfish_data.Chassis.chassis_dict.values():
        name = chassis.get_name()
        for sensor, temp in chassis.thermal.get_temperatures().items():
            # Using https://docs.python.org/3/library/uuid.html
            s = name + '-' + sensor
            uu = uuid.UUID(hashlib.md5(s.encode()).hexdigest())
            measurementList.append(
                    { "sensorUUID": uu,
                        "sensorValue": float(temp) })
        for fan, rpm in chassis.thermal.get_fans().items():
            rpml = rpm.split(None, 1)
            rpm = rpml[0]
            s = name + '-' + fan
            uu = uuid.UUID(hashlib.md5(s.encode()).hexdigest())
            measurementList.append(
                    { "sensorUUID": uu,
                        "sensorValue": float(rpm) })
        #for ps, volt in chassis.power.get_power().items():
            #measurementList.append(
                    #{ "sensorUUID": name + '-' + ps,
                        #"sensorValue": volt })

    record = {
        "uuid": str(mqttuuid),
        "timestamp": int(round(datetime.timestamp(datetime.now())*1000)),
        "measurementList": measurementList
        }

    for t in measurementList:
        for k,v in t.items():
            # remove that comment to check the sensors
            # print("key: " + str(k) + " value: " + str(v))
            pass

    sts = MessageSerializer(client)
    raw_bytes = sts.encode_record_with_schema_id(
                        cg.schema_id, record
                    )
    print(str(i) + ":Publishing via mqtt (topic:" + str(topic) + ") uuid: " + str(mqttuuid))
    mqttclient.publish(topic, raw_bytes)

    # Infinite loop - Redfish is slow so wait
    print("Sleeping " + str(SLEEP) + " seconds")
    time.sleep(SLEEP)
