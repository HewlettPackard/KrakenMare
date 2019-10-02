import os
import time
import json
from kafka import KafkaProducer
from kafka.errors import KafkaUnavailableError
import subprocess

# Time to wait between requests
SLEEP = 60
kafka_broker = "broker-1:9092"

# wait for Kafka broker to answer
producer = None

while not producer:
    time.sleep(5)
    try:
        producer = KafkaProducer(bootstrap_servers=[kafka_broker],value_serializer=lambda m: json.dumps(m).encode('utf8'))
    except KafkaUnavailableError:
        print "waiting for Kafka broker..."

# Infinite loop
rfdict = {}
while True:
    # Read formatted data from the server's chassis
    for line in subprocess.check_output(['redfish-client', '--insecure', 'chassis', 'getinfo', 'dl560g10']).splitlines():
        print('line: %s'%line)
        if ':' in line:
            key = line.split(":")[0]
            value = line.split(":")[1]
            print('key: %s value: %s'%(key.strip(),value.strip()))
            rfdict[key.strip()] = value.strip()

    # Write the json data to mqtt broker
    print('Publishing via Kafka')
    producer.send('ilo', rfdict)

    # Infinite loop - Redfish is slow so wait 1 min'
    time.sleep(SLEEP)
