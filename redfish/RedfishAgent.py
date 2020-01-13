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
import signal
import configparser
import random
import platform
import io
import uuid
import hashlib

# import special classes
import paho.mqtt.client as mqtt
from optparse import OptionParser
from fastavro import schemaless_writer, schemaless_reader
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import MessageSerializer
import redfish

# project imports
from version import __version__
from agentcommon import AgentCommon
from KrakenMareTriplet import KrakenMareTriplet

# START IBswitchSimulator class
class redfishAgent(AgentCommon):
    registered = False
    loggerName = None

    def __init__(self, configFile, debug, encrypt):
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

        self.sleepLoopTime = float(self.config.get("Others", "sleepLoopTime"))
        self.seedOutputDir = self.config.get("Others", "seedOutputDir")
        self.device_json_dir = self.config.get("Others", "deviceJSONdir")
        self.myDeviceMap = {}
        
        # MQTT setup
        self.myAgent_mqtt_encryption_enabled = encrypt
        self.myAgent_send_ts_data_topic = "ibswitch"
        
        self.myAgent_registration_request_topic = "agent-registration/" + self.myAgent_uid + "/request"
        
        self.myAgent_registration_response_topic = []
        myAgent_registration_response_topic = []
        myAgent_registration_response_topic.append("agent-registration/" + self.myAgent_uid + "/response")
        myAgent_registration_response_topic.append(0)
        self.myAgent_registration_response_topic.append(myAgent_registration_response_topic)
                
        self.myDevice_registration_response_topic = False
        
        # Redfish setup
        self.myAgent_redfish_ip = self.config.get("Redfish", "redfish_ip")
        self.myAgent_redfish_acc = self.config.get("Redfish", "redfish_acc")
        self.myAgent_redfish_pwd = self.config.get("Redfish", "redfish_pwd")
        self.mqttTopicRoot = "redfish/" + self.myAgent_redfish_ip.split("://")[1].split("/")[0] + '/'
        
        super().__init__(configFile, debug)
        

    # defines self.myMQTTregistered and self.myAgent_uuid
    def mqtt_on_message(self, client, userdata, message):
        print("on_message: message received on topic: %s" % message.topic)
        
        # since we transmit topic lists, this one has only one entry, and in this entry the first item is the topic name        
        if message.topic == self.myAgent_registration_response_topic[0][0]:
            print("message received: %s " % message.payload)
            # TO-DO, decoding with schema-registry requires magic byte in message
            #decode_msg_obj = self.msg_serializer.decode_message(message.payload)
            #print("registration-result with km UUID: %s" % decode_msg_obj["uuid"])
            
            r_bytes = io.BytesIO(message.payload)
            data = schemaless_reader(r_bytes, self.agent_register_response_schema)
            print("registration-result with KrakenMare UUID: %s" % data["uuid"])
            self.myMQTTregistered = True
            self.myAgent_uuid = data["uuid"]
            
            self.myDevice_registration_request_topic = "device-registration/" + str(self.myAgent_uuid) + "/request"
            
            # create new device response topic list with one entry [("topic name", qos)]
            self.myDevice_registration_response_topic = []
            myDevice_registration_response_topic = []
            myDevice_registration_response_topic.append("device-registration/" + str(self.myAgent_uuid) + "/response")
            myDevice_registration_response_topic.append(0)
            self.myDevice_registration_response_topic.append(myDevice_registration_response_topic)
        
            # add device registration response topic to enable re-subscription on mqtt re-connect (defined in the AgentCommon class).
            userdata.append(myDevice_registration_response_topic)
        
        # since we transmit topic lists, this one has only one entry, and in this entry the first item is the topic name 
        elif message.topic == self.myDevice_registration_response_topic[0][0]:
            print("message received: %s " % message.payload)
            r_bytes = io.BytesIO(message.payload)
            data = schemaless_reader(r_bytes, self.device_register_response_schema)
            self.myDeviceRegistered = True
            
        else:
            print("Unknown topic: " + str(message.topic) + " -- message received: %s " % message.payload)

    ################################################################################
    # create my device and sensor map
    def create_my_device_map(self):
        
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
    
        deviceTemplate["id"] = self.myAgent_redfish_ip
        deviceTemplate["name"] = self.myAgentName
        deviceTemplate["type"] = "Redfish iLO"
        deviceTemplate["location"] = cmc
        
        # assemble sensor information for device
        for chassis in redfish_data.Chassis.chassis_dict.values():
            name = chassis.get_name()
            
            # assemble sensor information for device
            for sensor in deviceTemplate["sensors"]:
                    sensor["id"] = switch["Node_GUID"] + "-" + sensor["name"]
                    
            for sensor, temp in chassis.thermal.get_temperatures().items():
                # Using https://docs.python.org/3/library/uuid.html
                s = topicroot + '-' + name + '-' + sensor
    
                # Interface with KrakenMareTriplet
                km.set_uuid(s)
                km.set_value(float(temp))
                km.print()
            
            # assemble sensor information for device
            deviceMap["devices"].append(deviceTemplate)
    
            for fan, rpm in chassis.thermal.get_fans().items():
                rpml = rpm.split(None, 1)
                rpm = rpml[0]
                s = topicroot + '-' + name + '-' + fan
    
                # Interface with KrakenMareTriplet
                km.set_uuid(s)
                km.set_value(float(rpm))
                km.print()
        
            # assemble sensor information for device
            deviceMap["devices"].append(deviceTemplate)
        
        return deviceMap
                
    # assemble and send simulated sensor data via MQTT (overwrites example method in parent class)
    def send_data(self):
        
        # Infinite loop
        i = 1
        
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
                                
                chassis_name = chassis.get_name()
                
                chassis_uuid = uuid.UUID(hashlib.md5((str(self.myAgent_uuid) + str(chassis_name)).encode()).hexdigest())
                    
                for sensor, temp in chassis.thermal.get_temperatures().items():
                    
                    sensor_uuid = uuid.UUID(hashlib.md5((str(self.myAgent_uuid) + chassis_name + sensor).encode()).hexdigest())
                            
                    record = {}
                    record["agentUuid"] = self.myAgent_uuid
                    record["agentId"] = self.myAgent_uid
                    record["sensorUuid"] = sensor_uuid
                    record["sensorValue"] = float(temp)
                    record["timestamp"] = timestamp
                    record["deviceUuid"] = chassis_uuid
                    record["sensorName"] = sensor
                    record["deviceId"] = chassis_name
                    
                    #print(record)
                    record_list.append(record)

                for fan, rpm in chassis.thermal.get_fans().items():
                    
                    rpml = rpm.split(None, 1)
                    rpm = rpml[0]
                    
                    sensor_uuid = uuid.UUID(hashlib.md5((str(self.myAgent_uuid) + chassis_name + fan).encode()).hexdigest())
                            
                    record = {}
                    #record["agentUuid"] = self.myAgent_uuid
                    #record["agentId"] = self.myAgent_uid
                    record["sensorUuid"] = sensor_uuid
                    record["sensorValue"] = float(rpm)
                    record["timestamp"] = timestamp
                    #record["deviceUuid"] = chassis_uuid
                    #record["sensorName"] = fan
                    #record["deviceId"] = chassis_name
                    
                    #print(record)
                    record_list.append(record)
                    
            for eachRecord in record_list:
                #print(str(eachRecord))
                if self.myAgent_debug == True:
                    print(str(i) + ":Publishing via mqtt (topic:self.myAgent_send_ts_data_topic): " + str(eachRecord))
                
                if i%1000 == 0:
                    print(str(i) + " messages published via mqtt (topic:%s)" % self.myAgent_send_ts_data_topic)
                
                self.mqtt_send_single_avro_ts_msg(self.myAgent_send_ts_data_topic, eachRecord)
                
                i += 1
            
        
            # Infinite loop
            time.sleep(self.sleepLoopTime)
                  
    
    def signal_handler(signal, frame):
        self.mqtt_close()
        sys.exit(0)
    
    # main method of IBswitchSimulator
    def run(self):
        
        # start mqtt client
        myLoopForever = False
        myCleanSession = False
        self.mqtt_init(self.myAgent_uid, self.myAgent_registration_response_topic, myLoopForever, myCleanSession)
        
        # register myself
        self.mqtt_registration(self.myAgent_registration_request_topic, self.myRegistrationData)
        
        # register my devices/sensors
        #self.myDeviceMap = self.create_my_device_map()
        #self.mqtt_device_registration(self.myDevice_registration_request_topic, self.myDevice_registration_response_topic, self.myDeviceMap)
        
        self.mqtt_close()
        
        
        self.mqtt_init(self.myAgent_uid, self.myAgent_registration_response_topic, myLoopForever, myCleanSession, self.myAgent_mqtt_encryption_enabled)
        # start sending data
        self.send_data()


# END IBswitchSimulator class
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
        "--encrypt",
        action="store_true",
        default=False,
        dest="encrypt",
        help="specify this option in order to encrypt the mqtt connection",
    )
    parser.add_option(
        "--logLevel",
        dest="logLevel",
        help="logger level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    (options, _) = parser.parse_args()

    option_dict = vars(options)

    # load container config
    myRedfishAgent = redfishAgent("RedfishAgent.cfg", debug=option_dict["debug"], encrypt=option_dict["encrypt"])
    signal.signal(signal.SIGINT, myRedfishAgent.signal_handler)
    myRedfishAgent.run()


if __name__ == "__main__":
    main()
