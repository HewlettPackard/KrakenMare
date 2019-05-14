import subprocess
import json
import time
import os
from random import *
import kafka
import paho.mqtt.client as mqtt
import uuid

mqtt_broker = "mosquitto"
kafka_broker = "broker-1"

# Register to the framework
registered = False;
agent_id = -1
agent_uuid = str(uuid.uuid4())
agent_name = "r1ib-simulator"

# wait for Kafka registration topic to exist
kafka_client = None
try:
    kafka_client = kafka.KafkaClient(kafka_broker)
except kafka.errors.KafkaUnavailableError:
    print "waiting for Kafka broker..."

while not kafka_client:
    time.sleep(1)
    try:
        kafka_client = kafka.KafkaClient(kafka_broker)
    except kafka.errors.KafkaUnavailableError:
        print "waiting for Kafka broker..."

while not "registration-result" in kafka_client.topics:
    print("waiting for registration-result topic...")
    time.sleep(1)
    # TODO: not sure how to refresh topic list, so recreate a client for now...
    kafka_client.close();
    kafka_client = kafka.KafkaClient(kafka_broker)

# TODO: we still need to wait: investigate why
time.sleep(60)

def on_log(client, userdata, level, buf):
    print("log: %s" % buf)

def on_registration_result(client, userdata, message):
    global registered, agent_id, agent_uuid
    print("message received: %s " % message.payload)
    print("message topic: %s" % message.topic)
    data = json.loads(message.payload)
    data_uuid = data.get("uuid")
    if data_uuid == agent_uuid:
        print("got registration-result with matching UUID: %s" % data_uuid)
        registered = True
        agent_id = data.get("id")
    else:
        print("ignoring registration-result with foreign UUID: %s" % data_uuid)

registration_client = mqtt.Client("RegistrationClient")
registration_client.on_log=on_log
registration_client.on_message = on_registration_result
registration_client.connect(mqtt_broker)
registration_client.loop_start()

registration_client.subscribe("registration-result")
# Generate a uuid to send over as the name
registration_payload = {}
registration_payload["name"] = agent_name
registration_payload["uuid"] = agent_uuid
data_out = json.dumps(registration_payload)
# use highest QoS for now
print("sending registration payload: %s" % data_out)
registration_client.publish("registration-request/r1ib", data_out, 2, True)

while not registered:
    time.sleep(1)
    print("waiting for registration result...")

registration_client.loop_stop()
print("registered with name '%s' and id '%d'" % (agent_name, agent_id))


client = mqtt.Client("DataClient")
client.connect(mqtt_broker)
# Infinite loop
while True:
   # Read formatted JSON data that describes the switches in the IRU (c stands for CMC)
   for cmc in ['r1i0c-ibswitch', 'r1i1c-ibswitch']:
      with open(cmc, 'r') as f:
         query_data = json.load (f)

      # For each switch found in the JSON data generate perfquery with -a to summarize the ports
      # This simulates a poor quality fabric in heavy use
      # Using random numbers on 0,1 we update three error counters as down below.
      # SymbolErrorCounter increments fastest
      # LinkedDownedCounter increments slower both fewer and less
      # PortXmitDiscards increments slowest both fewer and less
      # For data counters add randint[1000,4000]
      # for packet counters add randint[100,400]
      # Set time to milliseconds since the epoch for InfluxDB
      nowint = int(round(time.time() * 1000))

      for switch in query_data['Switch']:
         hca = str(switch['HCA'])
         port = str(switch['Port'])
         guid = str(switch['Node_GUID'])
         # Read in the old query outuput
         output = "/tmp/" + guid + ".perfquery.json"
         with open(output, 'r') as g:
            query_output = json.load (g)
         g.close()

         query_output['Name'] = agent_name
         query_output['Timestamp'] = nowint
         x = random()
         if x > .98:
            query_output['SymbolErrorCounter'] += 1000
         elif x > .88:
            query_output['SymbolErrorCounter'] += 10
         elif x > .78:
            query_output['SymbolErrorCounter'] += 1

         x = random()
         if x > .99:
            query_output['LinkDownedCounter'] += 100
         elif x > .89:
            query_output['LinkDownedCounter'] += 5
         elif x > .79:
            query_output['LinkDownedCounter'] += 1

         x = random()
         if x > .99:
            query_output['PortXmitDiscards'] += 10
         elif x > .89:
            query_output['PortXmitDiscards'] += 5
         elif x > .79:
            query_output['PortXmitDiscards'] += 2

         query_output['PortXmitData'] += randint(1000, 4000)
         query_output['PortRcvData'] += randint(1000, 4000)
         query_output['PortXmitPkts'] += randint(100, 400)
         query_output['PortRcvPkts'] += randint(100, 400)
         query_output['PortXmitWait'] += randint(100, 200)

# Write output to the next input
         with open(output, 'w') as g:
            json.dump(query_output, g)
         g.close()

# Write the json data to mqtt broker
         data_out = json.dumps(query_output)
         print('Publishing via mqtt')
         client.publish("ibswitch", data_out)

   # Infinite loop
   time.sleep(10)
