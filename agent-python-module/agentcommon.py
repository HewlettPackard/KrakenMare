#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@license: This Source Code Form is subject to the terms of the
@organization: Hewlett-Packard Enterprise (HPE)
@author: Torsten Wilde
"""

# import from OS
import json
import time
import os
import sys
import configparser
import random
import platform

# import special classes
import paho.mqtt.client as mqtt
from fastavro import schemaless_writer, schemaless_reader

import io
import uuid
import hashlib

# project imports
from version import __version__

from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import MessageSerializer

# START AgentCommon class
class AgentCommon:
    loggerName = None

    def __init__(self, configFile, debug):
        """
            Class init
            
        """

        self.myAgentCommonDebug = debug

        self.myMQTTregistered = False
        self.myDeviceRegistered = False
        
        self.loggerName = "agentcommon." + __version__ + ".log"

        self.config = self.checkConfigurationFile(
            configFile, ["Daemon", "Logger", "MQTT", "Schemaregistry"]
        )
        
        # MQTT setup
        self.mqtt_broker = self.config.get("MQTT", "mqtt_broker")
        self.mqtt_port = int(self.config.get("MQTT", "mqtt_port"))
        
        # schemas and schema registry setup
        conf = {
            "url": self.config.get("Schemaregistry", "url"),
            "ssl.ca.location": self.config.get("Schemaregistry", "ssl.ca.location"),
            "ssl.certificate.location": self.config.get("Schemaregistry", "ssl.certificate.location"),
            "ssl.key.location": self.config.get("Schemaregistry", "ssl.key.location"),
        }

        client = SchemaRegistryClient(conf)
        self.msg_serializer = MessageSerializer(client)
        
        # TO-DO: schema names could be in config file as list
        subject = "com-hpe-krakenmare-message-agent-RegisterRequest"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.agent_register_request_schema = cg.schema.schema
        self.agent_register_request_schema_id = cg.schema_id

        subject = "com-hpe-krakenmare-message-manager-RegisterResponse"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.agent_register_response_schema = cg.schema.schema
        self.agent_register_response_schema_id = cg.schema_id

        subject = "com-hpe-krakenmare-message-agent-SendTimeSeriesDruid"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.send_time_series_schema = cg.schema.schema
        self.send_time_series_schema_id = cg.schema_id
        
        subject = "com-hpe-krakenmare-message-agent-DeviceList"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.device_register_request_schema = cg.schema.schema
        self.device_register_request_schema_id = cg.schema_id
        
        subject = "com-hpe-krakenmare-message-manager-DeviceListResponse"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.device_register_response_schema = cg.schema.schema
        self.device_register_response_schema_id = cg.schema_id
        

    def checkConfigurationFile(
        self, configurationFileFullPath, sectionsToCheck, **options
    ):
        """
        Checks if the submitted.cfg configuration file is found
        and contains required sections
        configurationFileFullPath:
        full path to the configuration file (e.g. /home/agent/myConf.cfg)
        sectionsToCheck:
        list of sections in the configuration to be checked for existence
        """

        config = configparser.SafeConfigParser()

        if os.path.isfile(configurationFileFullPath) is False:
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

        if sectionsToCheck is not None:
            for section in sectionsToCheck:
                if not config.has_section(section):
                    print(
                        "ERROR: the configuration file is not correctly set \
                        - it does not contain required section: "
                        + section
                    )
                    print("Terminating ...")
                    sys.exit(2)

        return config

    ###########################################################################################
    # MQTT agent methods
    def mqtt_on_log(self, client, userdata, level, buf):
        if self.myAgentCommonDebug == True:
            print("on_log: %s" % buf)

    def mqtt_on_subscribe(self, client, userdata, mid, granted_qos):
        print("on_subscribe: Subscribed with message id (mid): " + str(mid))
        
    # The callback for when the client receives a CONNACK response from the server.
    def mqtt_on_connect(self, client, userdata, flags, rc):
        
        if self.myAgentCommonDebug == True:
            if (rc != 0):
                print("on_connect: Connection error: " + mqtt.connack_string(rc))
            else:
                print("on_connect: Connected with result code: " + mqtt.connack_string(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for topic in userdata and topic != False:
            self.client.subscribe(topic)

    def mqtt_on_disconnect(self, client, userdata, rc):
        if self.myAgentCommonDebug == True:
            print("on_disconnect: DisConnected result code: " + mqtt.connack_string(rc))
    
    def mqtt_on_publish(self, client, userdata, mid):
        if self.myAgentCommonDebug == True:
            print("on_publish: Published message with mid: " + str(mid))

          
    # this method takes care of Agent registration
    def mqtt_init(self, client_uid, topicList=[], loopForever = False, cleanSession = True):
        self.client = mqtt.Client(str(client_uid), userdata=topicList, clean_session=cleanSession)
        self.client.on_log = self.mqtt_on_log
        self.client.on_message = self.mqtt_on_message
        self.client.on_subscribe = self.mqtt_on_subscribe
        self.client.on_disconnect = self.mqtt_on_disconnect
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_publish = self.mqtt_on_publish
        print("connecting to mqtt broker:" + self.mqtt_broker)
        self.client.connect(self.mqtt_broker, self.mqtt_port)
        
        # subscribe to registration response topic
        result = -1
        while result != mqtt.MQTT_ERR_SUCCESS and topicList != False:
            #(result, mid) = self.client.subscribe([("ibswitch",0),("registration-result", 0)])
            print(topicList)
            (result, mid) = self.client.subscribe(topicList)
        
        # start listening loop
        if not loopForever:
            self.client.loop_start()
        else:
            self.client.loop_forever(retry_first_connection=True)
                    

    # this method takes care of Agent registration
    def mqtt_registration(self, requestTopic, RegistrationData={
            "uid": False,
            "type": "NONE",
            "name": "NONE",
            "description": "This is a fine description",
            "useSensorTemplate": False,
        }): 
               
        # publish registration data
        w_bytes = io.BytesIO()

        schemaless_writer(
            w_bytes, self.agent_register_request_schema, RegistrationData)

        raw_bytes = w_bytes.getvalue()

        # TO-DO: change to magic byte in Avro message on FM site
        #raw_bytes = self.msg_serializer.encode_record_with_schema_id(self.agent_register_request_schema_id, RegistrationData)

        # use highest QoS for now
        print("sending registration payload: --%s--" % raw_bytes)
        MQTTMessageInfo = self.client.publish(requestTopic, raw_bytes, 2, True)
        print("mqtt published with publishing code: " + mqtt.connack_string(MQTTMessageInfo.rc))
        if MQTTMessageInfo.is_published() == False:
            print("Waiting for message to be published.")
            MQTTMessageInfo.wait_for_publish()
            
        #self.client.publish("registration/" + self.myAgent_uid + "/request", raw_bytes, 2, True)

        while not self.myMQTTregistered:
            print("waiting for agent registration result...")
            time.sleep(1)
            '''
            if not self.myMQTTregistered:
                print("re-sending registration payload")
                self.client.publish(self.myAgent_registration_request_topic, raw_bytes, 2, True)
            '''
        print(
            "registered with uid '%s' and km-uuid '%s'"
            % (self.myAgent_uid, self.myAgent_uuid)
        )
        
        return self.myMQTTregistered

    # this method takes care of device/sensor registration after succesfull agent registration
    def mqtt_device_registration(self, deviceMQTTtopic, deviceMQTTresponseTopic, deviceMap):
        #print(self.myDeviceMap)
        result = -1
        while result != mqtt.MQTT_ERR_SUCCESS:
            (result, mid) = self.client.subscribe(deviceMQTTresponseTopic)
        
        # publish registration data
        w_bytes = io.BytesIO()

        schemaless_writer(
            w_bytes, self.device_register_request_schema, deviceMap)

        raw_bytes = w_bytes.getvalue()
        
        # use highest QoS for now
        print("sending device/sensor registration payload: --%s--" % raw_bytes)
        self.client.publish(deviceMQTTtopic, raw_bytes, 2, True)
        #self.client.publish("registration/" + self.myAgent_uid + "/request", raw_bytes, 2, True)

        while not self.myDeviceRegistered:
            print("waiting for device registration result...")
            time.sleep(1)
            if not self.myDeviceRegistered:
                print("re-sending device/sensor registration payload")
                self.client.publish(deviceMQTTtopic, raw_bytes, 2, True)

        #self.client.loop_stop()

    def mqtt_send_single_avro_ts_msg(self, topic, record):
        raw_bytes = self.msg_serializer.encode_record_with_schema_id(self.send_time_series_schema_id, record)
        self.client.publish(topic, raw_bytes)
    
    
    # close client method
    def mqtt_close(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("mqtt client loop stopped.")
        print("mqtt client disconnected")
    
    # example send method with simple (timestamp, uuid, value)
    def send_data(self):
        
        myCounter = 1
        
        while true:
            record_list = []
            
            # Assign time series values to the record to be serialized
            # here we read a list of 10 sensors at each timestamp
            
            # Set time to milliseconds since the epoch
            timestamp = int(round(time.time() * 1000))
                    # counter for send message count
            i = 1
            while i <= 10:
                record = {}
                record["sensorUuid"] = uuid.UUID(hashlib.md5("AgentCommon" + str(random.randint(1, 100001)).encode()).hexdigest())
                record["sensorValue"] = myCounter
                record["timestamp"] = timestamp
                record_list.append(record)
                i += 1
                myCounter += 1
            
            # publish collected time series data as individual (timestamp, sensor_uuid, value) records 
            for eachRecord in record_list:
                #print(str(eachRecord))
                if self.myAgent_debug == True:
                    print(str(i) + ":Publishing via mqtt (topic:%s)" % self.myAgent_send_ts_data_topic)
                
                self.mqtt_send_single_avro_ts_msg(self.myAgent_send_ts_data_topic, eachRecord)    
    
            # Infinite loop
            time.sleep(self.sleepLoopTime)

    # END MQTT agent methods
    ################################################################################

                
# END AgentCommon class
################################################################################
