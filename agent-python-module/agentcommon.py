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
import threading
import io
import uuid
import hashlib

# import special classes
import paho.mqtt.client as mqtt

# project imports
from version import __version__

from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import MessageSerializer

# START AgentCommon class
class AgentCommon:
    loggerName = None
    
    #myMQTTregistered = False
    #myMQTTderegistered = False
    myDeviceRegistered = False
    myByteBatch = []
    myCurrentSubtopic = 0
    myNumber_of_msg_send = 0
    myMessageCounter = 0

    def __init__(self, configFile, debug):
        """
            Class init
            
        """

        self.myAgentCommonDebug = debug
        
        self.loggerName = "agentcommon." + __version__ + ".log"

        self.config = self.checkConfigurationFile(
            configFile, ["Daemon", "Logger", "MQTT", "Schemaregistry"]
        )

        # MQTT setup
        self.mqtt_broker = self.config.get("MQTT", "mqtt_broker")
        self.mqtt_port = int(self.config.get("MQTT", "mqtt_port"))
        self.mqtt_broker_sec = self.config.get("MQTT", "mqtt_broker_sec")
        self.mqtt_port_sec = int(self.config.get("MQTT", "mqtt_port_sec"))
        self.mqtt_ca_certs = self.config.get("MQTT", "mqtt_ca_certs")
        self.mqtt_certfile = self.config.get("MQTT", "mqtt_certfile")
        self.mqtt_keyfile = self.config.get("MQTT", "mqtt_keyfile")

        # schemas and schema registry setup
        conf = {
            "url": self.config.get("Schemaregistry", "url"),
            "ssl.ca.location": self.config.get("Schemaregistry", "ssl.ca.location"),
            "ssl.certificate.location": self.config.get(
                "Schemaregistry", "ssl.certificate.location"
            ),
            "ssl.key.location": self.config.get("Schemaregistry", "ssl.key.location"),
        }

        client = SchemaRegistryClient(conf)
        self.msg_serializer = MessageSerializer(client)

        # TO-DO: schema names could be in config file as list
        subject = "com.hpe.krakenmare.message.agent.RegisterRequest"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.agent_register_request_schema = cg.schema.schema
        self.agent_register_request_schema_id = cg.schema_id

        subject = "com.hpe.krakenmare.message.manager.RegisterResponse"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.agent_register_response_schema = cg.schema.schema
        self.agent_register_response_schema_id = cg.schema_id

        subject = "com.hpe.krakenmare.message.agent.DeregisterRequest"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.agent_deregister_request_schema = cg.schema.schema
        self.agent_deregister_request_schema_id = cg.schema_id

        subject = "com.hpe.krakenmare.message.manager.DeregisterResponse"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.agent_deregister_response_schema = cg.schema.schema
        self.agent_deregister_response_schema_id = cg.schema_id

        subject = "com.hpe.krakenmare.message.agent.SendTimeSeriesDruid"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.send_time_series_schema = cg.schema.schema
        self.send_time_series_schema_id = cg.schema_id

        subject = "com.hpe.krakenmare.message.agent.DeviceList"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.device_register_request_schema = cg.schema.schema
        self.device_register_request_schema_id = cg.schema_id

        subject = "com.hpe.krakenmare.message.manager.DeviceListResponse"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.device_register_response_schema = cg.schema.schema
        self.device_register_response_schema_id = cg.schema_id
        
        subject = "com.hpe.krakenmare.message.agent.SendTimeSeriesDruidArray"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)
        self.send_time_series_druid_array = cg.schema.schema
        self.send_time_series_druid_array_id = cg.schema_id
        
    def setMqttNumberOfPublishingTopics(self, mqttNumberOfPublishingTopics):
        self.myAgentMqttNumberOfPublishingTopics = mqttNumberOfPublishingTopics
        
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

        config = configparser.ConfigParser()

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
        if self.myAgentCommonDebug == True:
            print("on_subscribe: Subscribed with message id (mid): " + str(mid))

    # The callback for when the client receives a CONNACK response from the server.
    def mqtt_on_connect(self, client, userdata, flags, rc):
        if self.myAgentCommonDebug == True:
            if rc != 0:
                print("on_connect: Connection error: " + mqtt.connack_string(rc))
            else:
                print(
                    "on_connect: Connected with result code: " + mqtt.connack_string(rc)
                )

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe(userdata)

    def mqtt_on_disconnect(self, client, userdata, rc):
        if self.myAgentCommonDebug == True:
            print("on_disconnect: DisConnected result code: " + mqtt.connack_string(rc))

    def mqtt_on_publish(self, client, userdata, mid):
        if self.myAgentCommonDebug == True:
            print("on_publish: Published message with mid: " + str(mid))

    # this method takes care of Agent registration
    def mqtt_init(
        self,
        client_uid,
        topicList=[],
        loopForever=False,
        cleanSession=True,
        encrypt=True,
    ):

        self.client = mqtt.Client(
            str(client_uid), userdata=topicList, clean_session=cleanSession
        )
        self.client.on_message = self.mqtt_on_message
        self.client.on_connect = self.mqtt_on_connect
        
        if self.myAgentCommonDebug == True:
            self.client.on_subscribe = self.mqtt_on_subscribe
            self.client.on_log = self.mqtt_on_log
            self.client.on_disconnect = self.mqtt_on_disconnect
            self.client.on_publish = self.mqtt_on_publish
            
        if encrypt == True:
            self.client.tls_set(
                ca_certs=self.mqtt_ca_certs,
                certfile=self.mqtt_certfile,
                keyfile=self.mqtt_keyfile,
            )
            print(
                "connecting with client id("
                + str(client_uid)
                + ") to mqtt broker (secured):"
                + self.mqtt_broker_sec
            )
            self.client.connect(self.mqtt_broker_sec, self.mqtt_port_sec)
        else:
            print(
                "connecting with client id("
                + str(client_uid)
                + ") to mqtt broker:"
                + self.mqtt_broker
            )
            
            self.client.connect(self.mqtt_broker, self.mqtt_port)

        # subscribe to registration response topic
        result = -1
        while result != mqtt.MQTT_ERR_SUCCESS and topicList != False:
            if self.myAgentCommonDebug == True:
                print(topicList)
                
            (result, mid) = self.client.subscribe(topicList)

        # start listening loop
        if not loopForever:
            self.client.loop_start()
        else:
            self.client.loop_forever(retry_first_connection=True)

    # this method takes care of Agent registration
    def mqtt_registration(
        self,
        requestTopic,
        RegistrationData={
            "uid": False,
            "type": "NONE",
            "name": "NONE",
            "description": "This is a fine description",
            "useSensorTemplate": False,
        },
    ):

        # publish registration data
        raw_bytes = self.msg_serializer.encode_record_with_schema_id(
            self.agent_register_request_schema_id, RegistrationData
        )

        # use highest QoS for now
        print("sending registration payload: --%s--" % raw_bytes)
        
        MQTTMessageInfo = self.client.publish(requestTopic[0], raw_bytes, requestTopic[1], True)
        print("mqtt published with publishing code: " + mqtt.connack_string(MQTTMessageInfo.rc))
        
        if MQTTMessageInfo.is_published() == False:
            print("Waiting for message to be published.")
            MQTTMessageInfo.wait_for_publish()

        while not self.myMQTTregistered:
            print("waiting for agent registration result...")
            time.sleep(1)
            """
            if not self.myMQTTregistered:
                print("re-sending registration payload")
                self.client.publish(self.myAgent_registration_request_topic, raw_bytes, 2, True)
            """
        print(
            "registered with uid '%s' and km-uuid '%s'"
            % (self.myAgent_uid, self.myAgent_uuid)
        )

        return self.myMQTTregistered

    def mqtt_deregistration(self, requestTopic, uuid):
        
        DeregistrationData={"uuid": uuid,} 

        # publish registration data
        raw_bytes = self.msg_serializer.encode_record_with_schema_id(self.agent_deregister_request_schema_id, DeregistrationData)

        # use QoS from requestTopic second entry, e.g. requestTopic[1]
        print("sending deregistration payload: --%s--" % raw_bytes)
        MQTTMessageInfo = self.client.publish(requestTopic[0], raw_bytes, requestTopic[1], True)
        print("mqtt published with publishing code: " + mqtt.connack_string(MQTTMessageInfo.rc))
        if MQTTMessageInfo.is_published() == False:
            print("Waiting for message to be published.")
            MQTTMessageInfo.wait_for_publish()

        while not self.myMQTTderegistered:
            print("waiting for agent deregistration result...")
            time.sleep(1)
            '''
            if not self.myMQTTregistered:
                print("re-sending registration payload")
                self.client.publish(self.myAgent_registration_request_topic, raw_bytes, 2, True)
            '''
        print(
            "deregistered with uid '%s' and km-uuid '%s'"
            % (self.myAgent_uid, self.myAgent_uuid)
        )
        
        return self.myMQTTderegistered

    # this method takes care of device/sensor registration after succesfull agent registration
    def mqtt_device_registration(
        self, deviceMQTTtopic, deviceMQTTresponseTopic, deviceMap
    ):
        # print(self.myDeviceMap)
        result = -1
        while result != mqtt.MQTT_ERR_SUCCESS:
            (result, mid) = self.client.subscribe(deviceMQTTresponseTopic)

        # publish registration data
        raw_bytes = self.msg_serializer.encode_record_with_schema_id(
            self.device_register_request_schema_id, deviceMap
        )

        # use highest QoS for now
        print("sending device/sensor registration payload: --%s--" % raw_bytes)
        self.client.publish(deviceMQTTtopic, raw_bytes, 2, True)

        while not self.myDeviceRegistered:
            print("waiting for device registration result...")
            time.sleep(1)
            if not self.myDeviceRegistered:
                print("re-sending device/sensor registration payload")
                self.client.publish(deviceMQTTtopic, raw_bytes, 2, True)

        # self.client.loop_stop()

    def mqtt_send_single_avro_ts_msg(self, topic, record):
        raw_bytes = self.msg_serializer.encode_record_with_schema_id(
            self.send_time_series_schema_id, record
        )
        self.client.publish(topic, raw_bytes)
        
    def mqtt_send_byte_batch_avro_ts_msg(self, topic, raw_bytes):
        self.client.publish(topic, raw_bytes)
    
    def mqtt_send_tripplet_batch(self, topic, record_list, sendNumberOfMessages, byteBatchSize, uuid):
        self.myByteBatchSize = byteBatchSize
        
        for eachRecord in record_list:
            if sendNumberOfMessages == self.myMessageCounter:
                print("All " + str(sendNumberOfMessages) + " messages published.")
                
                #publish any left over messages
                if byteBatchSize > 0:
                    myMQTT_ts_data = {
                        "tripletBatch": self.myByteBatch
                    }
                    raw_bytes = self.msg_serializer.encode_record_with_schema_id(self.send_time_series_druid_array_id, myMQTT_ts_data)
                    self.mqtt_send_byte_batch_avro_ts_msg("{:s}/{:d}".format(topic, self.myCurrentSubtopic), raw_bytes)
                
                self.mqtt_deregistration(self.myAgent_deregistration_response_topic[0], uuid)
                self.mqtt_close()
                sys.exit(0)
            
            #print(str(eachRecord))
            if self.myAgentCommonDebug == True:
                print(str(self.myMessageCounter) + ":Publishing via mqtt (topic:%s)" % (topic + "/" + str(self.myCurrentSubtopic)))
            
            if self.myMessageCounter%10000 == 0:
                print(str(self.myMessageCounter) + " messages published via mqtt (on %d subtopics from : %s)" % (self.myAgentMqttNumberOfPublishingTopics, topic))

            #self.mqtt_send_single_avro_ts_msg("{:s}/{:d}".format(self.myAgent_send_ts_data_topic, current_subtopic), eachRecord)
            #current_subtopic = (current_subtopic+1) if current_subtopic < self.myAgentMqttNumberOfPublishingTopics else 1
            
            # assemble ts data
            myMQTT_ts_data_triplet = {
                    "timestamp": eachRecord["timestamp"],
                    "sensorUuid": eachRecord["sensorUuid"],
                    "sensorValue": eachRecord["sensorValue"],
                    }
            
            if (byteBatchSize > 0):
                self.myByteBatch.append(myMQTT_ts_data_triplet)
                self.myMessageCounter += 1
            else:
                self.myByteBatch.append(self.msg_serializer.encode_record_with_schema_id(self.send_time_series_schema_id, myMQTT_ts_data_triplet))
            
            #print(sys.getsizeof(byte_batch))
            #print(byte_batch)
                                                                     
            if byteBatchSize == 0:
                self.mqtt_send_byte_batch_avro_ts_msg("{:s}/{:d}".format(topic, self.myCurrentSubtopic), self.myByteBatch.pop())
                
                if self.myAgentMqttNumberOfPublishingTopics > 1:
                    self.myCurrentSubtopic = (self.myCurrentSubtopic+1) if self.myCurrentSubtopic < self.myAgentMqttNumberOfPublishingTopics-1 else 0
                    
                self.myMessageCounter += 1

                self.myByteBatch = []
            elif sys.getsizeof(self.myByteBatch) >= byteBatchSize:
                if self.myAgentCommonDebug == True:
                    
                    print(
                        "Number of msg sent in one batch: "
                        + str(self.myMessageCounter - self.myNumber_of_msg_send)
                    )
                    print(
                        "Publishing to MQTT topic: "
                        + "{:s}/{:d}".format(topic, self.myCurrentSubtopic)
                    )
                    self.myNumber_of_msg_send = self.myMessageCounter

                myMQTT_ts_data = {"tripletBatch": self.myByteBatch}

                raw_bytes = self.msg_serializer.encode_record_with_schema_id(
                    self.send_time_series_druid_array_id, myMQTT_ts_data
                )
                self.mqtt_send_byte_batch_avro_ts_msg(
                    "{:s}/{:d}".format(topic, self.myCurrentSubtopic), raw_bytes
                )

                if self.myAgentMqttNumberOfPublishingTopics > 1:
                    self.myCurrentSubtopic = (
                        (self.myCurrentSubtopic + 1)
                        if self.myCurrentSubtopic
                        < self.myAgentMqttNumberOfPublishingTopics - 1
                        else 0
                    )

                self.myByteBatch = []
                
    # close client method
    def mqtt_close(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("mqtt client loop stopped.")
        print("mqtt client disconnected")

    # example send method with simple (timestamp, uuid, value)
    def send_data(self):

        myCounter = 1

        while True:
            record_list = []

            # Assign time series values to the record to be serialized
            # here we read a list of 10 sensors at each timestamp

            # Set time to milliseconds since the epoch
            timestamp = int(round(time.time() * 1000))
            # counter for send message count
            i = 1
            while i <= 10:
                record = {}
                record["sensorUuid"] = uuid.UUID(
                    hashlib.md5(
                        "AgentCommon" + str(random.randint(1, 100001)).encode()
                    ).hexdigest()
                )
                record["sensorValue"] = myCounter
                record["timestamp"] = timestamp
                record_list.append(record)
                i += 1
                myCounter += 1

            # publish collected time series data as individual (timestamp, sensor_uuid, value) records
            for eachRecord in record_list:
                # print(str(eachRecord))
                if self.myAgent_debug == True:
                    print(
                        str(i)
                        + ":Publishing via mqtt (topic:%s)"
                        % self.myAgent_send_ts_data_topic
                    )

                self.mqtt_send_single_avro_ts_msg(
                    self.myAgent_send_ts_data_topic, eachRecord
                )

            # Infinite loop
            time.sleep(self.sleepLoopTime)

    # END MQTT agent methods
    ################################################################################


# END AgentCommon class
################################################################################
