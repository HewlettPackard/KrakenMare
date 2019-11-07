#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@license: This Source Code Form is subject to the terms of the 
@organization: Hewlett-Packard Enterprise (HPE)
@author: Torsten Wilde
"""

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
import threading

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
class FanIn:
    registered = False
    loggerName = None

    def __init__(self, configFile, mode, debug):
        """
                Class init
        """

        self.sensors = []

        self.loggerName = "simulator.agent." + __version__ + ".log"

        self.config = self.checkConfigurationFile(
            configFile, ["Daemon", "Logger", "Kafka", "MQTT"]
        )

        # self.logger = self.helperFunctions.setLogger(self.config, self.loggerName)

        self.kafka_broker = self.config.get("Kafka", "kafka_broker")
        self.kafka_port = int(self.config.get("Kafka", "kafka_port"))
        self.kafkaProducerTopics = self.config.get("Kafka", "kafkaProducerTopic").split(
            ","
        )
        self.mqtt_broker = self.config.get("MQTT", "mqtt_broker")
        self.mqtt_port = int(self.config.get("MQTT", "mqtt_port"))
        self.mqttTopicList = self.config.get("MQTT", "mqttTopicList").split(",")
        self.sleepLoopTime = float(self.config.get("Others", "sleepLoopTime"))
        self.bootstrapServerStr = self.kafka_broker + ":" + str(self.kafka_port)

        # Register to the framework
        self.myFanInGateway_id = -1
        self.myFanInGateway_debug = debug
        self.myFanInGateway_uuid = str(uuid.uuid4())
        self.myFanInGatewayName = "FanIn-test1"
        
        # for thread safe counter
        self.myFanInGateway_threadLock = threading.Lock()
        
        self.myMQTTregistered = False
        self.kafka_producer = None
        self.kafka_consumer = None
        
        self.kafka_msg_counter = 0

    def resetLogLevel(self, logLevel):
        """
                Resets the log level 
        """
        self.logger = KrakenMareLogger().getLogger(self.loggerName, logLevel)

    def checkConfigurationFile(
        self, configurationFileFullPath, sectionsToCheck, **options
    ):
        """
                Checks if the submitted.cfg configuration file is found 
                and contains required sections

                configurationFileFullPath	 - full path to the configuration file (e.g. /home/agent/myConf.cfg)
                sectionsToCheck			   - list of sections in the configuration file that should be checked for existence 
        """

        config = configparser.SafeConfigParser()

        if os.path.isfile(configurationFileFullPath) == False:
            print(
                "ERROR: the configuration file "
                + configurationFileFullPath
                + " is not found"
            )
            print("Terminating ...")
            sys.exit(2)

        try:
            config.read(configurationFileFullPath)
        except Exception as e:
            print(
                "ERROR: Could not read the configuration file "
                + configurationFileFullPath
            )
            print("Detailed error description: "), e
            print("Terminating ...")
            sys.exit(2)

        if sectionsToCheck != None:
            for section in sectionsToCheck:
                if not config.has_section(section):
                    print(
                        "ERROR: the configuration file is not correctly set - it does not contain required section: "
                        + section
                    )
                    print("Terminating ...")
                    sys.exit(2)

        return config

    #######################################################################################
    # MQTT agent methods

    # connect to MQTT broker and subscribe to receive agent messages

    def mqtt_subscription(self):
        self.myMQTTtopic = "ibswitch"
        self.mqtt_client = mqtt.Client(client_id="FanInUUID", clean_session=True)
        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_disconnect = self.mqtt_on_disconnect
        self.mqtt_client.on_message = self.mqtt_on_agent_message
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
        # use '#' to subscribe to all topics
        self.mqtt_client.subscribe(self.myMQTTtopic, qos=0)
        self.mqtt_client.loop_forever(retry_first_connection=True)

        print(
            self.__class__.__name__
            + "."
            + inspect.currentframe().f_code.co_name
            + ": subscribed to MQTT for topics: "
            + self.myMQTTtopic
        )

    # The callback for when the client receives LOG response
    def mqtt_on_log(self, client, userdata, level, buf):
        if self.myFanInGateway_debug == True:
            print("log: %s" % buf)

    # The callback for when the client receives a CONNACK response from the server.
    def mqtt_on_connect(self, client, userdata, flags, rc):
        
        if self.myFanInGateway_debug == True:
            print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe(self.myMQTTtopic)

    def mqtt_on_disconnect(self, client, userdata, rc=0):
        if self.myFanInGateway_debug == True:
            print("DisConnected result code " + str(rc))

    # converts message to AVRO and sends message to Kafka (in batches)
    # TODO: do we need multiple threads here?
    # TODO: have processing method per client type OR topic for each sensor type to convert messages?
    def mqtt_on_agent_message(self, client, userdata, message):
        if message.topic == "ibswitch":
            
            with self.myFanInGateway_threadLock:
                self.kafka_msg_counter += 1
                
            if self.myFanInGateway_debug == True:
                print(str(self.kafka_msg_counter) + ":published to Kafka")
            
            if self.kafka_msg_counter%1000 == 0:
                print(str(self.kafka_msg_counter) + " messages published to Kafka")
            
            try:
                self.kafka_producer.produce("fabric", message.payload, on_delivery=self.kafka_producer_on_delivery)
            except BufferError:
                print('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %len(self.kafka_producer))
            
            # Serve delivery callback queue.
            # NOTE: Since produce() is an asynchronous API this poll() call
            #       will most likely not serve the delivery callback for the
            #       last produce()d message.
            self.kafka_producer.poll(0)
        else:
            if self.myFanInGateway_debug == True:
                print("Not ibswitch topic")

    # END MQTT agent methods
    #######################################################################################

    #######################################################################################
    # Kafka agent methods

    # Kafka error printer

    def kafka_producer_error_cb(self, err):
        print("error_cb", err)

    def kafka_producer_on_delivery(self, err, msg):
        if err:
            if self.myFanInGateway_debug == True:
                print('%% Message failed delivery: %s\n' % err)
        else:
            if self.myFanInGateway_debug == True:
                print('%% Message delivered to %s [%d] @ %d\n' % (msg.topic(), msg.partition(), msg.offset()))
    
    # connect to Kafka broker as producer to check topic 'myTopic'
    def kafka_check_topic(self, myTopic):
        print("Connecting as kafka consumer to check for topic: " + myTopic)
        test = False

        conf = {
            "bootstrap.servers": self.bootstrapServerStr,
            "client.id": socket.gethostname(),
            "socket.timeout.ms": 10,
            "error_cb": self.kafka_producer_error_cb,
            "message.timeout.ms": 10,
            "produce.offset.report": True,
        }

        while test == False:
            time.sleep(1)
            print("waiting for kafka producer to connect")

            try:
                # shouldn't be used directly: self.kafka_client = kafka.KafkaClient(self.kafka_broker)
                kafka_producer = KafkaProducer(conf)
                kafka_producer.list_topics(topic=myTopic, timeout=0.2)
                test = True
            except KafkaException as e:
                # print(e.args[0])
                print("waiting for " + myTopic + " topic...")

    # connect to Kafka broker as producer

    def kafka_producer_connect(self):
        test = False

        # conf = {'bootstrap.servers': self.bootstrapServerStr,'client.id': socket.gethostname(), 'socket.timeout.ms': 10,
        #          'error_cb': self.kafka_producer_error_cb, 'message.timeout.ms': 10}

        conf = {
            "bootstrap.servers": self.bootstrapServerStr,
            "socket.timeout.ms": 10,
            "error_cb": self.kafka_producer_error_cb,
            "message.timeout.ms": 10,
        }

        while test == False:
            time.sleep(1)
            print("waiting for kafka producer to connect")

            try:
                # shouldn't be used directly: self.kafka_client = kafka.KafkaClient(self.kafka_broker)
                self.kafka_producer = KafkaProducer(conf)
                self.kafka_producer.list_topics(timeout=0.2)
                test = True
            except KafkaException as e:
                print(e.args[0])
                print("waiting for Kafka brokers..." + self.bootstrapServerStr)

        print(inspect.currentframe().f_code.co_name + ": producer connected")

    # END Kafka agent methods
    #######################################################################################

    # main method of FanIn
    def run(self):
        # local and debug flag are not used from here at the moment

        # self.kafka_check_topic("registration-result")
        # self.kafka_check_topic("fabric")
        # self.mqtt_registration()
        self.kafka_producer_connect()
        # TODO: should be own process via process class (from multiprocessing import Process)
        self.mqtt_subscription()
        # while True:
        # 	pass
        # self.send_data("kafka")
        print("FanIn terminated")


### END IBswitchSimulator class ##################################################


def main():
    usage = "usage: %s --mode=redfish|mqtt" % sys.argv[0]
    parser = OptionParser(usage=usage, version=__version__)

    parser.add_option(
        "--mode", dest="modename", help="specify mode, possible modes are: redfish|mqtt"
    )
    parser.add_option(
        "--local",
        action="store_true",
        default=False,
        dest="local",
        help="specify this option in order to run in local mode",
    )
    parser.add_option(
        "--debug",
        action="store_true",
        default=False,
        dest="debug",
        help="specify this option in order to run in debug mode",
    )
    parser.add_option(
        "--logLevel",
        dest="logLevel",
        help="specify the logger level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    (options, _) = parser.parse_args()

    option_dict = vars(options)

    if options.local == True:
        # load development config to run outside of container
        myFanIn = FanIn("FanIn_dev.cfg", "local", debug=option_dict["debug"])
    else:
        # load container config
        myFanIn = FanIn("FanIn.cfg", "container", debug=option_dict["debug"])

    if options.logLevel:
        myFanIn.resetLogLevel(options.logLevel)

    myFanIn.run()


if __name__ == "__main__":
    main()
