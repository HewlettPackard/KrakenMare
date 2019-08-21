#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@license: This Source Code Form is subject to the terms of the 
@organization: Hewlett-Packard Enterprise (HPE)
@author: Torsten Wilde
'''

# import from OS
import subprocess
import json
import time
import os
import re
import sys
import string
import configparser
from random import *
from multiprocessing import Process, Lock
import socket
import inspect

# import special classes
import uuid
from confluent_kafka import Producer as KafkaProducer
from confluent_kafka import Consumer as KafkaConsumer, KafkaError, KafkaException
import paho.mqtt.client as mqtt
from optparse import OptionParser

# project imports
from version import __version__
import KrakenMareLogger


### START IBswitchSimulator class ##################################################
class FanIn():
	registered = False
	loggerName = None
	
	def __init__(self, configFile, mode):
		'''
			Class init
		'''
		
		self.sensors = []
		
		self.loggerName = "simulator.agent."+__version__+".log"
		
		self.config = self.checkConfigurationFile(configFile, ['Daemon', 'Logger', 'Kafka', 'MQTT'])
		
		#self.logger = self.helperFunctions.setLogger(self.config, self.loggerName)
		
		self.kafka_broker = self.config.get('Kafka', 'kafka_broker')
		self.kafka_port = int(self.config.get('Kafka', 'kafka_port'))
		self.kafkaProducerTopics = self.config.get('Kafka', 'kafkaProducerTopic').split(",")
		self.mqtt_broker = self.config.get('MQTT', 'mqtt_broker')
		self.mqtt_port = int(self.config.get('MQTT', 'mqtt_port'))
		self.mqttTopicList = self.config.get('MQTT', 'mqttTopicList').split(",")
		self.sleepLoopTime = float(self.config.get('Others', 'sleepLoopTime'))
		self.bootstrapServerStr = self.kafka_broker + ":" + str(self.kafka_port)

		
		# Register to the framework
		self.myAgent_id = -1
		self.myAgent_uuid = str(uuid.uuid4())
		self.myAgentName = "FanIn-test1"
		self.myMQTTregistered = False
		self.kafka_producer = None
		self.kafka_consumer = None
	
			
	def resetLogLevel(self, logLevel):
		"""
			Resets the log level 
		"""
		self.logger = KrakenMareLogger().getLogger(self.loggerName, logLevel)
	
	
	def checkConfigurationFile(self, configurationFileFullPath, sectionsToCheck, **options):
		'''
			Checks if the submitted.cfg configuration file is found 
			and contains required sections
			
			configurationFileFullPath	 - full path to the configuration file (e.g. /home/agent/myConf.cfg)
			sectionsToCheck			   - list of sections in the configuration file that should be checked for existence 
		'''
		
		config = configparser.SafeConfigParser()
		
		if(os.path.isfile(configurationFileFullPath) == False):
			print("ERROR: the configuration file " + configurationFileFullPath + " is not found")
			print("Terminating ...")
			sys.exit(2)
		
		try:
			config.read(configurationFileFullPath)
		except Exception as e:	 
			print("ERROR: Could not read the configuration file " + configurationFileFullPath)
			print("Detailed error description: "), e
			print("Terminating ...")
			sys.exit(2)
		
		if(sectionsToCheck != None):
			for section in sectionsToCheck:
				if(not config.has_section(section)):
					print("ERROR: the configuration file is not correctly set - it does not contain required section: " + section)
					print("Terminating ...")
					sys.exit(2)
		
		return config
	

	#######################################################################################
	# MQTT agent methods
	def mqtt_on_log(self, client, userdata, level, buf):
		print("log: %s" % buf)
	
	
	# The callback for when the client receives a CONNACK response from the server.
	def mqtt_on_connect(self, client, userdata, flags, rc):
		print("Connected with result code "+str(rc))
		
		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		self.client.subscribe("#")
		
	
	
	# connect to MQTT broker and subscribe to receive agent messages
	def mqtt_subscription(self):
		self.mqtt_client = mqtt.Client("FanInUUID")
		#self.mqtt_client.on_log = self.mqtt_on_log
		self.mqtt_client.on_connect = self.mqtt_on_connect
		self.mqtt_client.on_message = self.mqtt_on_agent_message
		self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
		self.mqtt_client.subscribe("#") # use '#' to subscribe to all topics
		self.mqtt_client.loop_start()
		
		print(inspect.currentframe().f_code.co_name + ": subscribed to MQTT.")
		
	
	# converts message to AVRO and sends message to Kafka (in batches)
	# TODO: do we need multiple threads here?
	# TODO: have processing method per client type OR topic for each sensor type to convert messages?
	# TODO: or should the MQTT agent convert message into our schema before sending via MQTT?
	def mqtt_on_agent_message(self, client, userdata, message):
		print("message topic: %s" % message.topic)
		
		""" Data format from simulator
		{"name": "PortSelect", "type": "int", "doc": "For switches -a flag gives PortSelect of 255"},
		{"name": "SymbolErrorCounter", "type": "int"},
		{"name": "LinkErrorRecoveryCounter", "type": "int"},
		{"name": "LinkDownedCounter", "type": "int"},
		{"name": "PortRcvErrors", "type": "int"},
		{"name": "PortRcvRemotePhysicalErrors", "type": "int"},
		{"name": "PortRcvSwitchRelayErrors", "type": "int"},
		{"name": "PortXmitDiscards", "type": "int"},
		{"name": "PortXmitConstraintErrors", "type": "int"},
		{"name": "PortRcvConstraintErrors", "type": "int"},
		{"name": "LocalLinkIntegrityErrors", "type": "int"},
		{"name": "ExcessiveBufferOverrunErrors", "type": "int"},
		{"name": "VL15Dropped", "type": "int"},
		{"name": "PortXmitData", "type": "long"},
		{"name": "PortRcvData", "type": "long"},
		{"name": "PortXmitPkts", "type": "long"},
		{"name": "PortRcvPkts", "type": "long"},
		{"name": "PortXmitWait", "type": "int"},
		{"name": "Timestamp", "type": "long", "logicalType": "timestamp-millis", "doc": "Number of milliseconds since the epoch"},
		{"name": "GUID", "type": "string", "doc": "Globally Unique Identifier in hex but treated as string"},
		{"name": "Name", "type": "string", "doc": "Name of agent that is sending data"}
		"""
				
		#process message
		if message.topic == "ibswitch":
			kafka_message = {}
			
			#print("message received: %s " % message.payload)
			
			myMQTTmessage = json.loads(message.payload)
			
			for key, value in myMQTTmessage.items():
				print(str(key) + ':' + str(value))
				# reassemble message to Kafka avro syntax
				"""
				"fields": [
				    {
				      "name": "uuid",
				      "type": "int"
				    },
				    {
				      "name": "measurement-list",
				      "type": {
				            "type": "record",
				            "name": "sensor",
				            "fields": [
				              {
				                 "name": "sensorUUID",
				                 "type": "int"
				                },
				                {
				                 "name": "values",
				                 "type": "map",
				                 "values": "float"
				                }]
				       }
				    }]
				"""
				
			# missing agent uuid
			agentUUID = myMQTTmessage['Name']
			timestamp = myMQTTmessage['Timestamp']
			kafka_message[agentUUID] = {}
			kafka_message[agentUUID]['measurement-list'] = {}
			
			# go through sensors and add measurements for each sensor
			for key, value in myMQTTmessage.items():
				
				# make up sensor uuid
				sensorUUID = myMQTTmessage['GUID'] + "-" + key
				
				if not sensorUUID in kafka_message[agentUUID]['measurement-list']:
					kafka_message[agentUUID]['measurement-list'][sensorUUID] = {}
				
				if not timestamp in kafka_message[agentUUID]['measurement-list'][sensorUUID]:
					kafka_message[agentUUID]['measurement-list'][sensorUUID][timestamp] = []
			
				kafka_message[agentUUID]['measurement-list'][sensorUUID][timestamp] = value


			print("Kafka message:")
			print(kafka_message)
			"""
				{'r1ib-simulator': {'measurement-list': {'0x0800690000005E60-PortSelect': {1566582290496: 255}, 
															'0x0800690000005E60-SymbolErrorCounter': {1566582290496: 2},
															'0x0800690000005E60-LinkErrorRecoveryCounter': {1566582290496: 0},
															'0x0800690000005E60-LinkDownedCounter': {1566582290496: 7},
															'0x0800690000005E60-PortRcvErrors': {1566582290496: 0},
															'0x0800690000005E60-PortRcvRemotePhysicalErrors': {1566582290496: 0},
															'0x0800690000005E60-PortRcvSwitchRelayErrors': {1566582290496: 3},
															'0x0800690000005E60-PortXmitDiscards': {1566582290496: 300},
															'0x0800690000005E60-PortXmitConstraintErrors': {1566582290496: 0},
															'0x0800690000005E60-PortRcvConstraintErrors': {1566582290496: 0},
															'0x0800690000005E60-LocalLinkIntegrityErrors': {1566582290496: 0},
															'0x0800690000005E60-ExcessiveBufferOverrunErrors': {1566582290496: 0},
															'0x0800690000005E60-VL15Dropped': {1566582290496: 0},
															'0x0800690000005E60-PortXmitData': {1566582290496: 18246776},
															'0x0800690000005E60-PortRcvData': {1566582290496: 18106365},
															'0x0800690000005E60-PortXmitPkts': {1566582290496: 117447},
															'0x0800690000005E60-PortRcvPkts': {1566582290496: 113729},
															'0x0800690000005E60-PortXmitWait': {1566582290496: 822841},
															'0x0800690000005E60-Timestamp': {1566582290496: 1566582290496},
															'0x0800690000005E60-GUID': {1566582290496: '0x0800690000005E60'},
															'0x0800690000005E60-Name': {1566582290496: 'r1ib-simulator'}}}}

			"""
		
	# END MQTT agent methods   
	#######################################################################################
	
	
	#######################################################################################
	# Kafka agent methods
	
	# Kafka error printer
	def kafka_producer_error_cb(self, err):
		print('error_cb', err)
		
	# connect to Kafka broker as producer to check topic 'myTopic'
	def kafka_check_topic(self, myTopic):
		
		print("Connecting as kafka consumer to check for topic: " + myTopic)
		test = False
		
		conf = {'bootstrap.servers': self.bootstrapServerStr,'client.id': socket.gethostname(), 'socket.timeout.ms': 10,
                  'error_cb': self.kafka_producer_error_cb, 'message.timeout.ms': 10}
		
		while test == False:
			time.sleep(1)
			print("waiting for kafka producer to connect")
			
			try:
				#shouldn't be used directly: self.kafka_client = kafka.KafkaClient(self.kafka_broker)
				kafka_producer = KafkaProducer(conf)
				kafka_producer.list_topics(topic=myTopic, timeout=0.2)
				test = True
			except KafkaException as e:
				#print(e.args[0])
				print("waiting for " + myTopic + " topic...")


	# connect to Kafka broker as producer
	def kafka_producer_connect(self):
		test = False
		
		conf = {'bootstrap.servers': self.bootstrapServerStr,'client.id': socket.gethostname(), 'socket.timeout.ms': 10,
                  'error_cb': self.kafka_producer_error_cb, 'message.timeout.ms': 10}
		
		while test == False:
			time.sleep(1)
			print("waiting for kafka producer to connect")
			
			try:
				#shouldn't be used directly: self.kafka_client = kafka.KafkaClient(self.kafka_broker)
				self.kafka_producer = KafkaProducer(conf)
				self.kafka_producer.list_topics(timeout=0.2)
				test = True
			except KafkaException as e:
				print(e.args[0])
				print("waiting for Kafka brokers..." + self.bootstrapServerStr)
		
		print(inspect.currentframe().f_code.co_name + ": producer connected")
		
	# END Kafka agent methods
	#######################################################################################
	
	# send simulated sensor data via MQTT or Kafka, depending on command line flag
	def send_data_to_kafka(self):
		
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
					output = self.seedOutputDir + "/" + guid + ".perfquery.json"
					with open(output, 'r') as g:
						query_output = json.load (g)
					g.close()
		
					query_output['Name'] = self.myAgentName
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
					
					data_out = json.dumps(query_output).encode('utf-8')
					
					self.kafka_producer.send("fabric", data_out)
						
			# Infinite loop
			time.sleep(self.sleepLoopTime)
			
	
	# main method of FanIn
	def run(self, debug):
		# local and debug flag are not used from here at the moment
				
		#self.kafka_check_topic("registration-result")
		#self.kafka_check_topic("fabric")
		#self.mqtt_registration()
		self.kafka_producer_connect()
		self.mqtt_subscription() # TODO: should be own process via process class (from multiprocessing import Process)
		while True:
			pass
		#self.send_data("kafka")
	
### END IBswitchSimulator class ##################################################	


def main():
	usage = ("usage: %s --mode=kafka|mqtt" % sys.argv[0])
	parser = OptionParser(usage=usage, version=__version__)
	
	parser.add_option("--mode", dest="modename", help="specify mode, possible modes are: kafka|mqtt")
	parser.add_option("--local", action="store_true", default=False, dest="local",
					  help = "specify this option in order to run in local mode")
	parser.add_option("--debug", action="store_true", default=False, dest="debug",
					  help = "specify this option in order to run in debug mode")
	parser.add_option("--logLevel", dest="logLevel",
						  help="specify the logger level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
	
	(options, _) = parser.parse_args()
	
	option_dict = vars(options)
	
	if (options.local == True):
		# load development config to run outside of container
		myFanIn = FanIn('FanIn_dev.cfg', 'local')
	else:
		# load container config
		myFanIn = FanIn('FanIn.cfg', 'container')
	
	if(options.logLevel):
		myFanIn.resetLogLevel(options.logLevel)
	
	myFanIn.run(debug=option_dict['debug'])
	

if __name__ == '__main__':
	main()