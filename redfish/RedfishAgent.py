#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
(C) Copyright 2020 Hewlett Packard Enterprise Development LP.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

# import from OS
import json
import time
import os
import sys
import signal
import configparser
import random
import platform
import io
import uuid
import hashlib
import requests
import logging

# import special classes
import paho.mqtt.client as mqtt
from optparse import OptionParser
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import MessageSerializer
import redfish

# project imports
from version import __version__
from agentcommon import AgentCommon

# START RedfishAgent class
class RedfishAgent(AgentCommon):
    myMQTTregistered = False
    myMQTTderegistered = False
    loggerName = None

    def __init__(self, configFile, debug, encrypt, numberOfTopics, batching=False, sleepLoopTime=False):
        """
            Class init
            
        """

        self.loggerName = "redfish.agent." + __version__ + ".log"
        
        # AgentCommon class method
        self.config = self.checkConfigurationFile(
            configFile, ["Others", "MQTT", "Redfish"]
        )

        self.myAgentName = "RedfishAgent"
        self.myAgent_debug = debug
        self.MQTTbatching = batching
               
        # Agent uid as provided by the discovery mechanism.
        # for now use the hostname and random number to insure we are always unique
        # used for Agent registration and MQTT client id
        self.myAgent_uid = platform.node() + self.myAgentName + str(random.randint(1, 100001))
        
        # uuid comes from the central framework manager
        self.myAgent_uuid = -1

        # assemble my agent registration data
        self.myRegistrationData = {
            "uid": self.myAgent_uid,
            "name": self.myAgentName,
            "type": "redfishAgent",
            "description": "This is a fine description",
            "useSensorTemplate": False,
        }

        # set sleepLoopTime from cfg file or use command line provided value
        if sleepLoopTime == False:
            self.sleepLoopTime = float(self.config.get("Others", "sleepLoopTime"))
        else:
            self.sleepLoopTime = float(sleepLoopTime)
        
        self.seedOutputDir = self.config.get("Others", "seedOutputDir")
        self.device_json_dir = self.config.get("Others", "deviceJSONdir")
        self.sendNumberOfMessages = self.config.get("Others", "sendNumberOfMessages")
        
        self.myDeviceMap = {}
        self.myDeviceSensorUUIDsMap = {}
        
        # MQTT setup
        self.myAgent_mqtt_encryption_enabled = encrypt

        if batching == True:
            self.batch_size = self.config.get("MQTT", "mqtt_batch_size")
            if self.batch_size == "":
                self.batch_size = 0
            else:
                self.batch_size = int(self.batch_size)
        else:
            self.batch_size = 0
        
        self.myAgent_send_ts_data_topic = "ibswitch"
        
        # create agent registration request topic list with one entry [("topic name", qos)]
        self.myAgent_registration_request_topic = []
        myAgent_registration_request_topic = []
        myAgent_registration_request_topic.append(
            "agent-registration/" + self.myAgent_uid + "/request"
        )
        myAgent_registration_request_topic.append(2)
        self.myAgent_registration_request_topic.append(
            myAgent_registration_request_topic
        )

        # create agent registration response topic list with one entry [("topic name", qos)]
        self.myAgent_registration_response_topic = []
        myAgent_registration_response_topic = []
        myAgent_registration_response_topic.append(
            "agent-registration/" + self.myAgent_uid + "/response"
        )
        myAgent_registration_response_topic.append(2)
        self.myAgent_registration_response_topic.append(
            myAgent_registration_response_topic
        )

        self.myDevice_registration_response_topic = False
        
        # Redfish setup
        self.myAgent_redfish_ip = self.config.get("Redfish", "redfish_ip")
        self.myAgent_redfish_acc = self.config.get("Redfish", "redfish_acc")
        self.myAgent_redfish_pwd = self.config.get("Redfish", "redfish_pwd")
        self.mqttTopicRoot = "redfish/" + self.myAgent_redfish_ip.split("://")[1].split("/")[0] + '/'
        
        super().__init__(configFile, debug)
        
        # set number of topics in parent class and set self.myBatchCounter for each topic
        self.setMqttNumberOfPublishingTopics(int(numberOfTopics))

    # defines self.myMQTTregistered and self.myAgent_uuid
    def mqtt_on_message(self, client, userdata, message):
        print("on_message: message received on topic: %s" % message.topic)
        
        # since we transmit topic lists, this one has only one entry, and in this entry the first item is the topic name        
        if message.topic == self.myAgent_registration_response_topic[0][0]:
            if self.myAgent_debug == True:
                print("message received: %s " % message.payload)
            
            data = self.msg_serializer.decode_message(message.payload)
            
            if self.myAgent_debug == True:
                print("registration-result with KrakenMare UUID: %s" % data["uuid"])
                
            self.myMQTTregistered = True
            self.myAgent_uuid = data["uuid"]
            
            # create agent deregistration request topic list with one entry [("topic name", qos)]
            self.myAgent_deregistration_request_topic = []
            myAgent_deregistration_request_topic = []
            myAgent_deregistration_request_topic.append(
                "agent-deregistration/" + str(self.myAgent_uuid) + "/request"
            )
            myAgent_deregistration_request_topic.append(2)
            self.myAgent_deregistration_request_topic.append(
                myAgent_deregistration_request_topic
            )

            self.myDevice_registration_request_topic = (
                "device-registration/" + str(self.myAgent_uuid) + "/request"
            )

            # create new device response topic list with one entry [("topic name", qos)]
            self.myDevice_registration_response_topic = []
            myDevice_registration_response_topic = []
            myDevice_registration_response_topic.append(
                "device-registration/" + str(self.myAgent_uuid) + "/response"
            )
            myDevice_registration_response_topic.append(2)
            self.myDevice_registration_response_topic.append(
                myDevice_registration_response_topic
            )

            # create new agent de-registration response topic list with one entry [("topic name", qos)]
            self.myAgent_deregistration_response_topic = []
            myAgent_deregistration_response_topic = []
            myAgent_deregistration_response_topic.append(
                "agent-deregistration/" + str(self.myAgent_uuid) + "/response"
            )
            myAgent_deregistration_response_topic.append(2)
            self.myAgent_deregistration_response_topic.append(
                myAgent_deregistration_response_topic
            )

            # add device registration response topic to enable re-subscription on mqtt re-connect (defined in the AgentCommon class).
            userdata.append(myDevice_registration_response_topic)
            userdata.append(myAgent_deregistration_response_topic)
        
        # since we transmit topic lists, this one has only one entry, and in this entry the first item is the topic name
        elif message.topic == self.myDevice_registration_response_topic[0][0]:
            
            if self.myAgent_debug:
                print("message: %s " % message.payload)
            
            data = self.msg_serializer.decode_message(message.payload)
            
            if self.myAgent_debug:
                print("message: %s " % data)
            
            #set myDeviceSensorUUIDsMap with registred uuids
            if data["uuid"] == self.myAgent_uuid:
                print("processing my device and sensor registration")
                self.myDeviceSensorUUIDsMap = data["deviceUuids"]
                #print(self.myDeviceSensorUUIDsMap)
            
            self.myDeviceRegistered = True
            
            if self.myAgent_debug:
                print("Final device and sensor UUID map")
                print(self.myDeviceSensorUUIDsMap)
                print("==========================================")
                for device in self.myDeviceSensorUUIDsMap:
                    print(self.myDeviceSensorUUIDsMap[device])
            
            print("Devices registered")

        # since we transmit topic lists, this one has only one entry, and in this entry the first item is the topic name
        elif message.topic == self.myAgent_deregistration_response_topic[0][0]:
            self.myMQTTderegistered = True
            print("message: %s " % message.payload)
            data = self.msg_serializer.decode_message(message.payload)
            print(str(data))
            
        else:
            print("Unknown topic: " + str(message.topic) + " -- message received: %s " % message.payload)

    ################################################################################
    # create my device and sensor map
    def create_my_device_map(self):
        print("Creating my device map")
        
        # store for final device and sensor map according to InfinibandAgent.json syntax
        deviceMap = {}
        
        deviceMap["uuid"] = str(self.myAgent_uuid)
        deviceMap["devices"] = []
        
        # read device json template
        with open(self.device_json_dir + "/iLODevice.json", "r") as f:
                deviceTemplate = json.load(f)
        
        # set my informations in device/sensor map
        # go through high level devices and add each switch as device (deviceUid = myAgentUuid + device guid
        if self.myAgent_redfish_acc == "":
            simulator = True
            enforceSSL = False
        else:
            simulator = False
            enforceSSL = True
        try:

            redfish.config.TORTILLADEBUG = False
            requests.packages.urllib3.disable_warnings()
            redfish.config.CONSOLE_LOGGER_LEVEL = logging.CRITICAL
            redfish_data = redfish.connect(self.myAgent_redfish_ip,
                                        self.myAgent_redfish_acc,
                                        self.myAgent_redfish_pwd,
                                        verify_cert=False,
                                        simulator=simulator,
                                        enforceSSL=enforceSSL)
        except redfish.exception.RedfishException as e:
            sys.stderr.write(str(e.message))
            sys.stderr.write(str(e.advices))
            print("Sleeping " + str(self.sleepLoopTime) + " seconds")
            time.sleep(self.sleepLoopTime)
            pass
        
        # assemble sensor information for device
        #"uuid": null, "id": "guid+metricname", "name": "PortSelect", "type": "Counter", "valueRangeMin": 0.0, "valueRangeMax": 255.0, "currentCollectionFrequency": 0.1, "storageTime": 1}
        
        #got through all devices       
        for chassis in redfish_data.Chassis.chassis_dict.values():
            # reset deviceTemplate for each new device
            deviceTemplate = {}
            
            chassisName = chassis.get_name()
            deviceTemplate["uuid"] = None
            deviceTemplate["id"] = str(self.myAgent_uuid) + "-" + str(chassisName)
            deviceTemplate["name"] = str(chassisName)
            deviceTemplate["type"] = "Redfish iLO"
            deviceTemplate["location"] = "unknown"
            deviceTemplate["sensors"] = []
            
            # assemble sensor information for device                 
            for sensorName, value in chassis.thermal.get_temperatures().items():
                # reset sensorTemplate for each new sensor
                sensorTemplate = {}
                
                sensorTemplate["uuid"] = None
                sensorTemplate["id"] =  str(self.myAgent_uuid) + "-" + str(chassisName) + "-" + str(sensorName)
                sensorTemplate["name"] = str(sensorName) 
                sensorTemplate["type"] = "Counter"
                sensorTemplate["valueRangeMin"] = 0.0 
                sensorTemplate["valueRangeMax"] = 100.0
                sensorTemplate["currentCollectionFrequency"] = 1.0
                sensorTemplate["storageTime"] = 1             

                deviceTemplate["sensors"].append(sensorTemplate)
            
            # assemble sensor information for device
            for sensorName, value in chassis.thermal.get_fans().items():
                # reset sensorTemplate for each new sensor
                sensorTemplate = {}
                
                sensorTemplate["uuid"] = None
                sensorTemplate["id"] =  str(self.myAgent_uuid) + "-" + str(chassisName) + "-" + str(sensorName)
                sensorTemplate["name"] = str(sensorName) 
                sensorTemplate["type"] = "Counter"
                sensorTemplate["valueRangeMin"] = 0.0 
                sensorTemplate["valueRangeMax"] = 100.0
                sensorTemplate["currentCollectionFrequency"] = 1.0
                sensorTemplate["storageTime"] = 1             

                deviceTemplate["sensors"].append(sensorTemplate)
            
            # assemble sensor information for device
            deviceMap["devices"].append(deviceTemplate)
            
        if self.myAgent_debug:
            print("Finished creating my device map")
            print(deviceMap)
        
        return deviceMap
                
    # assemble and send simulated sensor data via MQTT (overwrites example method in parent class)
    def send_data(self):
        print("Started sending data loop")
        # Infinite loop
        
        # For each switch found in the JSON data ,
        # generate sensor uuid from has of seed sensor uuids + cmc + guid
        # each is a device
        """"for switch in query_data["Switch"]:
            switch_guid = str(switch["Node_GUID"])

            # set device UUID from registration
            device_uuid[cmc][switch_guid] = self.myDeviceSensorUUIDsMap[switch_guid]["uuid"]
            
            sensor_uuid[cmc][switch_guid] = {}

            for ibmetric in ibmetrics:

                # set sensor UUIID from registration
                sensor_uuid[cmc][switch_guid][ibmetric] = self.myDeviceSensorUUIDsMap[switch_guid]["sensorUuids"][switch_guid+"-"+ibmetric]
                
                if ibmetric in ["SymbolErrorCounter", "PortXmitData"]:
                    print(
                        switch_guid+"-"+ibmetric
                        + ":"
                        + str(sensor_uuid[cmc][switch_guid][ibmetric])
                    )
        """
        
        # baremetal nodes have python 3.6 hence we don't have time_ns. Here time is a floating point number
        self.timet0 = time.time()
        while True:
            connected = False
            
            if self.myAgent_redfish_acc == "":
                simulator = True
                enforceSSL = False
            else:
                simulator = False
                enforceSSL = True
                
            while not connected:
                try:
                    redfish.config.TORTILLADEBUG = False
                    requests.packages.urllib3.disable_warnings()
                    redfish.config.CONSOLE_LOGGER_LEVEL = logging.CRITICAL
                    redfish_data = redfish.connect(self.myAgent_redfish_ip,
                                                self.myAgent_redfish_acc,
                                                self.myAgent_redfish_pwd,
                                                verify_cert=False,
                                                simulator=simulator,
                                                enforceSSL=enforceSSL)
                    connected = True
                    timestamp = int(round(time.time() * 1000))
                    # reset record_list for each new redfish query
                    record_list = []
                except redfish.exception.RedfishException as e:
                        sys.stderr.write(str(e.message))
                        sys.stderr.write(str(e.advices))
                        print("Sleeping " + str(self.sleepLoopTime) + " seconds")
                        time.sleep(self.sleepLoopTime)
                        continue
        
            for chassis in redfish_data.Chassis.chassis_dict.values():
                                
                chassisName = chassis.get_name()
                
                #{'60dcdc0b-9ee7-447e-9aee-1944e4a6bafe-Computer System Chassis': {'uuid': UUID('637d4053-e962-4687-a8d1-87fd352dcc0e'), 'sensorUuids': {'60dcdc0b-9ee7-447e-9aee-1944e4a6bafe-Computer System Chassis-18-VR P1 Mem 1': UUID('947e869b-e883-4359-b989-59045cc63b77'), 
                chassis_uuid = self.myDeviceSensorUUIDsMap[str(self.myAgent_uuid) + "-" + str(chassisName)]["uuid"]
                
                for sensor, value in chassis.thermal.get_temperatures().items():
                    sensorName = str(self.myAgent_uuid) + "-" + str(chassisName) + "-" + str(sensor)                    
                    sensor_uuid = self.myDeviceSensorUUIDsMap[str(self.myAgent_uuid) + "-" + str(chassisName)]["sensorUuids"][sensorName]
                    record = {}
                    
                    record["sensorUuid"] = sensor_uuid
                    record["sensorValue"] = float(value)
                    record["timestamp"] = timestamp
                    
                    #print(record)
                    record_list.append(record)

                for sensor, value in chassis.thermal.get_fans().items():
                    sensorName = str(self.myAgent_uuid) + "-" + str(chassisName) + "-" + str(sensor)                    
                    sensor_uuid = self.myDeviceSensorUUIDsMap[str(self.myAgent_uuid) + "-" + str(chassisName)]["sensorUuids"][sensorName]
                    
                    valuelist = value.split(None, 1)
                    value = valuelist[0]
                                                
                    record = {}
                    record["sensorUuid"] = sensor_uuid
                    record["sensorValue"] = float(value)
                    record["timestamp"] = timestamp
                    
                    #print(record)
                    record_list.append(record)
            
            # send messages
            self.mqtt_send_triplet_batch(
                    self.myAgent_send_ts_data_topic,
                    record_list,
                    self.sendNumberOfMessages,
                    self.batch_size,
                    self.myAgent_uuid,
                    self.timet0
                )
        
            # Infinite loop
            time.sleep(self.sleepLoopTime)
                  
    
    def signal_handler(self, signal, frame):
        self.mqtt_deregistration(self.myAgent_deregistration_request_topic[0], self.myAgent_uuid)
        
        while self.myMQTTderegistered == False:
            print("Waiting for de-registration response message.")
            sleep(2)
        
        self.mqtt_close()
        sys.exit(0)
    
    # main method of RedfishAgent
    def run(self):
        
        # start mqtt client
        myLoopForever = False
        myCleanSession = False
        self.mqtt_init(self.myAgent_uid, self.myAgent_registration_response_topic, myLoopForever, myCleanSession, self.myAgent_mqtt_encryption_enabled)
        
        # register myself
        self.mqtt_registration(self.myAgent_registration_request_topic[0], self.myRegistrationData)
        
        # register my devices/sensors
        self.myDeviceMap = self.create_my_device_map()
        self.mqtt_device_registration(self.myDevice_registration_request_topic, self.myDevice_registration_response_topic, self.myDeviceMap)
        
        # start sending data
        self.send_data()


# END RedfishAgent class
################################################################################


def main():
    
    usage = "usage: %s" % sys.argv[0]
    parser = OptionParser(usage=usage, version=__version__)

    parser.add_option(
        "--debug",
        action="store_true",
        default=False,
        dest="debug",
        help="specify this option in order to run in debug mode",
    )
    parser.add_option(
        "--numberOfTopic",
        dest="numberOfTopic",
        default=False,
        help="specify this option in order to publish to multiple topics (# of topics (need to be able to divide 16 by this,e.g. --numberOfTopic=2), defaults to 1",
    )
    parser.add_option(
        "--sleepLoopTime",
        dest="sleepLoopTime",
        default=False,
        help="specify this option in order to overwrite sleepLoopTime value in the cfg file.",
    )
    parser.add_option(
        "--encrypt",
        action="store_true",
        default=False,
        dest="encrypt",
        help="specify this option in order to encrypt the mqtt connection",
    )
    parser.add_option(
        "--batching",
        action="store_true",
        default=False,
        dest="batching",
        help="specify this option to enable batching on MQTT connection",
    )
    parser.add_option(
        "--logLevel",
        dest="logLevel",
        help="logger level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    (options, _) = parser.parse_args()

    option_dict = vars(options)
    
    if options.numberOfTopic:
        numberOfMqttTopics = option_dict["numberOfTopic"]
    else:
        numberOfMqttTopics = 1

    # load container config
    myRedfishAgent = RedfishAgent("RedfishAgent.cfg", debug=option_dict["debug"], encrypt=option_dict["encrypt"], numberOfTopics=numberOfMqttTopics,
        batching=option_dict["batching"],
        sleepLoopTime=option_dict["sleepLoopTime"])
    
    signal.signal(signal.SIGINT, myRedfishAgent.signal_handler)
    myRedfishAgent.run()


if __name__ == "__main__":
    main()
