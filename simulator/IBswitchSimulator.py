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

# import special classes
import uuid
import kafka
from kafka import KafkaProducer
from kafka import KafkaConsumer
import paho.mqtt.client as mqtt
from optparse import OptionParser

# project imports
from version import __version__


### START IBswitchSimulator class ##################################################
class IBswitchSimulator():
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
		self.mqtt_broker = self.config.get('MQTT', 'mqtt_broker')
		self.mqtt_port = int(self.config.get('MQTT', 'mqtt_port'))
		self.sleepLoopTime = float(self.config.get('Others', 'sleepLoopTime'))
		self.seedOutputDir = self.config.get('Others', 'seedOutputDir')
		self.bootstrapServerStr = self.kafka_broker + ":" + str(self.kafka_port)
		
		# Register to the framework
		self.myAgent_id = -1
		self.myAgent_uuid = str(uuid.uuid4())
		self.myAgentName = "r1ib-simulator"
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
	
	
	# TODO: for now we listen to any response, not only ours
	# defines self.myMQTTregistered and self.myAgent_id
	def mqtt_on_registration_result(self, client, userdata, message):
		
		print("message received: %s " % message.payload)
		print("message topic: %s" % message.topic)
		data = json.loads(message.payload)
		data_uuid = data.get("uuid")
		if data_uuid == self.myAgent_uuid:
			print("got registration-result with matching UUID: %s" % data_uuid)
			self.myMQTTregistered = True
			self.myAgent_id = data.get("id")
		else:
			print("ignoring registration-result with foreign UUID: %s" % data_uuid)
		
	
	def mqtt_registration(self):
		registration_client = mqtt.Client("RegistrationClient")
		registration_client.on_log = self.mqtt_on_log
		registration_client.on_message = self.mqtt_on_registration_result
		registration_client.connect(self.mqtt_broker)
		registration_client.loop_start()
	
		registration_client.subscribe("registration-result")
		
		# Generate a uuid to send over as the name
		registration_payload = {}
		registration_payload["name"] = self.myAgentName
		registration_payload["uuid"] = self.myAgent_uuid
		data_out = json.dumps(registration_payload)
		
		# use highest QoS for now
		print("sending registration payload: %s" % data_out)
		registration_client.publish("registration-request/r1ib", data_out, 2, True)
		
		while not self.myMQTTregistered:
		    time.sleep(1)
		    print("waiting for registration result...")
		
		registration_client.loop_stop()
		print("registered with name '%s' and id '%d'" % (self.myAgentName, self.myAgent_id))
	# END MQTT agent methods   
	#######################################################################################
	
	
    #######################################################################################
    # Kafka agent methods
	
	# connect to Kafka broker as consumer (check topic list)
	def kafka_check_topic(self, topic):
		
		print("Connecting as kafka consumer to check for topic: " + topic)
		
		while not self.kafka_consumer:
			try:
				#shouldn't be used directly: self.kafka_client = kafka.KafkaClient(self.kafka_broker)
				self.kafka_consumer = KafkaConsumer(bootstrap_servers=[self.bootstrapServerStr], consumer_timeout_ms=10000)
			except (kafka.errors.KafkaUnavailableError, kafka.errors.NoBrokersAvailable) as e:
				print("waiting for Kafka broker...")
	
		while not topic in self.kafka_consumer.topics():
			print("waiting for " + topic + " topic...")
			time.sleep(1)
			# TODO: not sure how to refresh topic list, so recreate a client for now...
			self.kafka_consumer.close();
			self.kafka_consumer = KafkaConsumer(bootstrap_servers=[self.bootstrapServerStr], consumer_timeout_ms=10000)
	
		# TODO: we still need to wait: investigate why
		self.kafka_consumer.close();
	

	# connect to Kafka broker as producer
	def kafka_producer_connect(self):
		
		while not self.kafka_producer:
			time.sleep(1)
			print("waiting for kafka producer to connect")
			
			try:
				#shouldn't be used directly: self.kafka_client = kafka.KafkaClient(self.kafka_broker)
				self.kafka_producer = KafkaProducer(bootstrap_servers=[self.bootstrapServerStr], value_serializer=lambda x : json.dumps(x).encode('utf-8'))
			except kafka.errors.KafkaUnavailableError:
				print("waiting for Kafka broker..." + self.kafka_broker)
		
		print("kafka producer connected")

    # END Kafka agent methods
    #######################################################################################
    
    # send simulated sensor data via MQTT or Kafka, depending on command line flag
	def send_data(self, pubsubType):
		
		if (pubsubType == "mqtt"):
			client = mqtt.Client("DataClient")
			client.connect(self.mqtt_broker, self.mqtt_port)
		elif (pubsubType == "kafka"):
			self.kafka_check_topic("fabric")
		else:
			print("Unknown Pub/Sub type selected: " + pubsubType)
			sys.exit(-1)
		
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
					
					if (pubsubType == "mqtt"):
						print("Publishing via mqtt")
						data_out = json.dumps(query_output).encode('utf-8')
						client.publish("ibswitch", data_out)
					elif (pubsubType == "kafka"):
						print("Publishing via kafka")
						self.kafka_producer.send("fabric", query_output)
					else:
						print("error: shouldn't be here")
						sys.exit(-1)
			
			# Infinite loop
			time.sleep(self.sleepLoopTime)
    
    # END Kafka agent methods
    #######################################################################################
    
    
	# main method of IBswitchSimulator
	def run(self, mode, local, debug):
		# local and debug flag are not used from here at the moment
		
		self.kafka_check_topic("registration-result")		
		
		if mode == "mqtt":
			print("mqtt mode")
			#self.mqtt_registration()
			self.send_data("mqtt")
		else:
			print("Kafka mode")
			self.kafka_producer_connect()
			self.send_data("kafka")
	
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
	
	if(option_dict['modename'] == None):
		print("Incorrect usage")
		parser.print_help()
		sys.exit(0)
	
	if (options.local == True):
		# load development config to run outside of container
		myIBswitchSimulator = IBswitchSimulator('IBswitchSimulator_dev.cfg', 'local')
	else:
		# load container config
		myIBswitchSimulator = IBswitchSimulator('IBswitchSimulator.cfg', 'container')
	
	if(options.logLevel):
		myIBswitchSimulator.resetLogLevel(options.logLevel)

	if(options.modename == 'kafka'):
		myIBswitchSimulator.run("kafka", local=option_dict['local'], debug=option_dict['debug'])
					
	elif(options.modename == 'mqtt'):
		myIBswitchSimulator.run("mqtt", local=option_dict['local'], debug=option_dict['debug'])
			
	else:
		print("ERROR: Unknown action command.")
		sys.exit(2)


if __name__ == '__main__':
	main()