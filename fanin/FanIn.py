#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@license: This Source Code Form is subject to the terms of the 
@organization: Hewlett-Packard Enterprise (HPE)
@author: Torsten Wilde
"""

# import from OS
import subprocess
import time
import os
import sys
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
from optparse import OptionParser

# project imports
from version import __version__
import KrakenMareLogger
from agentcommon import AgentCommon


### START IBswitchSimulator class ##################################################
class FanIn(AgentCommon):
    registered = False
    loggerName = None
# All time is in seconds as float. We use time_ns to get highest resolution
    timet0 = float(time.time_ns())/1000000000
    MsgCount = 0

    def __init__(self, configFile, debug, encrypt):
        """
                Class init
        """

        self.sensors = []
        self.mqttTopicList = []

        self.loggerName = "simulator.agent." + __version__ + ".log"

        self.config = self.checkConfigurationFile(
            configFile, ["Daemon", "Logger", "Kafka", "MQTT"]
        )

        # self.logger = self.helperFunctions.setLogger(self.config, self.loggerName)

        self.kafka_broker = self.config.get("Kafka", "kafka_broker")
        self.kafka_port = int(self.config.get("Kafka", "kafka_port"))
        self.kafkaProducerTopic = self.config.get("Kafka", "kafkaProducerTopic")
        self.myFanIn_mqtt_encryption_enabled = encrypt
        self.mqtt_broker = self.config.get("MQTT", "mqtt_broker")
        self.mqtt_port = int(self.config.get("MQTT", "mqtt_port"))
        
        # create topic list: [ ("topicName1", int(qos1)),("topicName2", int(qos2)) ]
        #                    [ ("ibswitch", 0), ("redfish", 0)]
        
        for item in self.config.get("MQTT", "mqttTopicList").split(","):
            addValue = []
            value = item.split(":")
            addValue.append(value[0])
            addValue.append(int(value[1]))
            self.mqttTopicList.append(addValue)
            #print(self.mqttTopicList)
            #print(type(self.mqttTopicList))
            
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
        self.kafka_msg_ack_received = 0
        
        super().__init__(configFile, debug)

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
    # sends MQTT messages to Kafka (in batches)
    # TODO: do we need multiple threads here?
    # TODO: have processing method per client type OR topic for each sensor type to convert messages?
    def mqtt_on_message(self, client, userdata, message):
        if self.myFanInGateway_debug == True:
                print("On mqtt message start")
                
        if message.topic == self.mqttTopicList[0][0]:
            # first topic in config file ("ibswitch")            

            if self.kafka_msg_counter%1000 == 0:
                deltat   = float(time.time_ns())/1000000000 - FanIn.timet0
                deltaMsg = self.kafka_msg_counter - FanIn.MsgCount
                FanIn.MsgCount = self.kafka_msg_counter
                FanIn.timet0  = float(time.time_ns())/1000000000
                print(str(self.kafka_msg_counter) + " messages published to Kafka, rate = {:.2f} msg/sec".format(deltaMsg/deltat))
            
            try:
                self.kafka_producer.produce(self.kafkaProducerTopic, message.payload, on_delivery=self.kafka_producer_on_delivery)
                with self.myFanInGateway_threadLock:
                    self.kafka_msg_counter += 1
                
                if self.myFanInGateway_debug == True:
                    print(str(self.kafka_msg_counter) + ":published to Kafka")
                
                if self.kafka_msg_counter%1000 == 0:
                    print(str(self.kafka_msg_counter) + " messages published to Kafka")
                    
            except BufferError as e1:
                print('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %len(self.kafka_producer))
            except KafkaException as e2:
                print("MQTT message not published to Kafka! Cause is ERROR:")
                print(e2)
            
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
        print("KAFKA_PROD_CALLBACK_ERR : {:s}".format(str(err)))

    def kafka_producer_on_delivery(self, err, msg):
        if err:
            print('KAFKA_MESSAGE_CALLBACK_ERR : %% Message failed delivery: %s - to %s [%d] @ %d\n' % (err, msg.topic(), msg.partition(), msg.offset()))
        else:
            self.kafka_msg_ack_received += 1
            #if self.kafka_msg_ack_received%500 == 0:
                #print("KAFKA_MESSAGE_CALLBACK : num msg ACKed by KAFKA = {:d} of {:d} MQTT msg received and sent to KAFKA".format(self.kafka_msg_ack_received, self.kafka_msg_counter))
            if self.myFanInGateway_debug == True :
                print('%% Message delivered to %s [%d] @ %d\n' % (msg.topic(), msg.partition(), msg.offset()))

    # connect to Kafka broker as producer to check topic 'myTopic'
    def kafka_check_topic(self, myTopic):
        print("Connecting as kafka consumer to check for topic: " + myTopic)
        test = False

        conf = {
            "bootstrap.servers": self.bootstrapServerStr,
            "client.id": socket.gethostname() + "topicCheck",
            "error_cb": self.kafka_producer_error_cb
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

        conf = {
            "bootstrap.servers": self.bootstrapServerStr,
            "client.id": socket.gethostname(),
            "error_cb": self.kafka_producer_error_cb,
            "linger.ms": 1000,
            "message.max.bytes": 256000
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

        print(self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + ": producer connected")

    # END Kafka agent methods
    #######################################################################################

    # main method of FanIn
    def run(self):
        # local and debug flag are not used from here at the moment

        # self.kafka_check_topic("registration-result")
        self.kafka_check_topic(self.kafkaProducerTopic)
        # self.mqtt_registration()
        self.kafka_producer_connect()
        # TODO: should be own process via process class (from multiprocessing import Process)
        # generate list of mqtt topics to subscribe, used in initial connection and to re-subscribe on re-connect
        
        mqttSubscriptionTopics=self.mqttTopicList
        
        # start mqtt client
        myLoopForever = False
        myCleanSession = True
        self.mqtt_init(self.myFanInGateway_uuid, mqttSubscriptionTopics, myLoopForever, myCleanSession, self.myFanIn_mqtt_encryption_enabled)
        
        # start listening to data
        #self.mqtt_subscription()
        while True:
            time.sleep(1)
            self.kafka_producer.poll(0)
            print("KAFKA_MESSAGE_CALLBACK : num msg ACKed by KAFKA = {:d} of {:d} MQTT msg received and sent to KAFKA".format(self.kafka_msg_ack_received, self.kafka_msg_counter))
        print("FanIn terminated")


### END IBswitchSimulator class ##################################################


def main():
    usage = "usage: %s " % sys.argv[0]
    parser = OptionParser(usage=usage, version=__version__)

    parser.add_option(
        "--encrypt",
        action="store_true",
        default=False,
        dest="encrypt",
        help="specify this option in order to encrypt the mqtt connection",
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

    myFanIn = FanIn("FanIn.cfg", debug=option_dict["debug"], encrypt=option_dict["encrypt"])

    if options.logLevel:
        myFanIn.resetLogLevel(options.logLevel)

    myFanIn.run()


if __name__ == "__main__":
    main()
