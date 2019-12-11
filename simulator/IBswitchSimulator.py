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

# project imports
from version import __version__
from agentcommon import AgentCommon

# START IBswitchSimulator class
class IBswitchSimulator(AgentCommon):
    registered = False
    loggerName = None

    def __init__(self, configFile, debug):
        """
            Class init
            
        """

        self.loggerName = "simulator.agent." + __version__ + ".log"
        
        # AgentCommon class method
        self.config = self.checkConfigurationFile(
            configFile, ["Others"]
        )

        self.myAgentName = "IBSwitchSimulator"
        self.myAgent_debug = debug
        
        # Agent uid as provided by the discovery mechanism.
        # for now use the hostname and random number to insure we are always unique
        # used for Agent registration and MQTT client id
        self.myAgent_uid = platform.node() + str(random.randint(1, 100001))
        
        # uuid comes from the central framework manager
        self.myAgent_uuid = -1

        # assemble my agent registration data
        self.myRegistrationData = {
            "uid": self.myAgent_uid,
            "name": self.myAgentName,
            "type": "simulatorAgent",
            "description": "This is a fine description",
            "useSensorTemplate": False,
        }

        self.sleepLoopTime = float(self.config.get("Others", "sleepLoopTime"))
        self.seedOutputDir = self.config.get("Others", "seedOutputDir")
        self.device_json_dir = self.config.get("Others", "deviceJSONdir")
        self.myDeviceMap = {}
        
        # MQTT setup
        self.myAgent_send_ts_data_topic = "ibswitch"
        
        self.myAgent_registration_request_topic = "agent-registration/" + self.myAgent_uid + "/request"
        
        self.myAgent_registration_response_topic = []
        myAgent_registration_response_topic = []
        myAgent_registration_response_topic.append("agent-registration/" + self.myAgent_uid + "/response")
        myAgent_registration_response_topic.append(0)
        self.myAgent_registration_response_topic.append(myAgent_registration_response_topic)
                
        self.myDevice_registration_response_topic = False
        
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
        
        # read device json template
        with open(self.device_json_dir + "/InfinibandDevice.json", "r") as f:
                deviceTemplate = json.load(f)
           
        deviceMap["uuid"] = str(self.myAgent_uuid)
        deviceMap["devices"] = []
        
        # set my informations in device/sensor map
        # go through high level devices and add each switch as device (deviceUid = myAgentUuid + device guid
        for cmc in ["r1i0c-ibswitch", "r1i1c-ibswitch"]:
            
            with open(cmc, "r") as f:
                query_data = json.load(f)

            # For each switch found in the JSON data ,
            # assemble map for each device and store it in myDeviceMap
            for switch in query_data["Switch"]:
                deviceTemplate["id"] = switch["Node_GUID"]
                deviceTemplate["name"] = cmc + "-ib"
                deviceTemplate["type"] = "Infiniband Switch"
                deviceTemplate["location"] = cmc
                
                # assemble sensor information for device 'switch'
                for sensor in deviceTemplate["sensors"]:
                    sensor["id"] = switch["Node_GUID"] + "-" + sensor["name"]
                
                deviceMap["devices"].append(deviceTemplate)
        
        return deviceMap
                
    ################################################################################
    # read seed files used as starting values for simulator and populate my seed hash map
    def seed_simulator_map(self):
        seedMap = {}
        
        # read JSON data describing switches in the IRU (c stands for CMC)
        for cmc in ["r1i0c-ibswitch", "r1i1c-ibswitch"]:
            seedMap[cmc] = {}
            
            with open(cmc, "r") as f:
                query_data = json.load(f)

            # For each switch device found in the JSON data ,
            # add sensors and starting value
            for switch in query_data["Switch"]:
                guid = switch["Node_GUID"]
                seedMap[cmc][guid] = {}

                # Read in the old query output
                output = self.seedOutputDir + "/" + guid + ".perfquery.json"
                with open(output, "r") as infile:
                    query_output = json.load(infile)
                infile.close()

                seedMap[cmc][guid] = query_output
                seedMap[cmc][guid]["Name"] = self.myAgentName + ":" + str(self.myAgent_uid)

        # done
        return seedMap
        
    
    # assemble and send simulated sensor data via MQTT (overwrites example method in parent class)
    def send_data(self):
               
        # counter for send message count
        i = 1

        # Create a dictionary of the 18 IB metrics names
        ibmetrics = [
            "SymbolErrorCounter",
            "PortXmitData"
            ]
        
        """ibmetrics = [
            "PortSelect",
            "SymbolErrorCounter",
            "LinkErrorRecoveryCounter",
            "LinkDownedCounter",
            "PortRcvErrors",
            "PortRcvRemotePhysicalErrors",
            "PortRcvSwitchRelayErrors",
            "PortXmitDiscards",
            "PortXmitConstraintErrors",
            "PortRcvConstraintErrors",
            "LocalLinkIntegrityErrors",
            "ExcessiveBufferOverrunErrors",
            "VL15Dropped",
            "PortXmitData",
            "PortRcvData",
            "PortXmitPkts",
            "PortRcvPkts",
            "PortXmitWait",
        ]"""
        
        """ Sample data record for a timestamp using the new flat version:
        record = {
            "uuid": str(self.myAgent_uuid),
            "timestamp": 1570135369000,
            "sensorUuid": "afbfa80d-cd9d-487a-841c-6da12b10c6d0",
            "sensorValue": 0.0,
            "deviceUuid" : "afbfd80d-cd9d-487a-841c-6da12b10c6d0",
        }
        """
        
        # read JSON data describing switches in the IRU (c stands for CMC)
        device_uuid = {}
        sensor_uuid = {}
        
        # assemble UUID map
        # TODO: replace with device/sensor registration UUIDs from Framework Manager
        for cmc in ["r1i0c-ibswitch", "r1i1c-ibswitch"]:
            device_uuid[cmc] = {}
            sensor_uuid[cmc] = {}
            
            with open(cmc, "r") as f:
                query_data = json.load(f)

            # For each switch found in the JSON data ,
            # generate sensor uuid from has of seed sensor uuids + cmc + guid
            # each is a device
            for switch in query_data["Switch"]:
                switch_guid = str(switch["Node_GUID"])
                
                #device UUID
                device_uuid[cmc][switch_guid] = uuid.UUID(hashlib.md5((str(self.myAgent_uuid) + switch_guid).encode()).hexdigest())
                
                sensor_uuid[cmc][switch_guid] = {}

                for ibmetric in ibmetrics:
                    
                    #sensor UUIID
                    sensor_uuid[cmc][switch_guid][ibmetric] = uuid.UUID(hashlib.md5((str(self.myAgent_uuid) + str(device_uuid[cmc][switch_guid]) + ibmetric).encode()).hexdigest())
                    if ibmetric in ["SymbolErrorCounter", "PortXmitData"]:
                        print(ibmetric + ":" + str(sensor_uuid[cmc][switch_guid][ibmetric]))

        switchSimulatorSeedMap = self.seed_simulator_map()

        # Infinite loop
        while True:
                             
            # read JSON data describing switches in the IRU
            for cmc in switchSimulatorSeedMap:

                # go through sensors for device
                for switchGUID in switchSimulatorSeedMap[cmc]:
                    
                    # reset record_list for each new switch
                    record_list = []
                    
                    # Set time to milliseconds since the epoch
                    timestamp = int(round(time.time() * 1000))
                    
                    x = random.random()
                    if x > 0.98:
                        switchSimulatorSeedMap[cmc][switchGUID]["SymbolErrorCounter"] += 1000
                    elif x > 0.88:
                        switchSimulatorSeedMap[cmc][switchGUID]["SymbolErrorCounter"] += 10
                    elif x > 0.78:
                        switchSimulatorSeedMap[cmc][switchGUID]["SymbolErrorCounter"] += 1

                    x = random.random()
                    if x > 0.99:
                        switchSimulatorSeedMap[cmc][switchGUID]["LinkDownedCounter"] += 100
                    elif x > 0.89:
                        switchSimulatorSeedMap[cmc][switchGUID]["LinkDownedCounter"] += 5
                    elif x > 0.79:
                        switchSimulatorSeedMap[cmc][switchGUID]["LinkDownedCounter"] += 1

                    x = random.random()
                    if x > 0.99:
                        switchSimulatorSeedMap[cmc][switchGUID]["PortXmitDiscards"] += 10
                    elif x > 0.89:
                        switchSimulatorSeedMap[cmc][switchGUID]["PortXmitDiscards"] += 5
                    elif x > 0.79:
                        switchSimulatorSeedMap[cmc][switchGUID]["PortXmitDiscards"] += 2

                    # Assign the simulator values to the record to be serialized
                    for ibmetric in ibmetrics:
                        record = {}
                        record["agentUuid"] = self.myAgent_uuid
                        record["agentId"] = self.myAgent_uid
                        record["sensorUuid"] = sensor_uuid[cmc][switchGUID][ibmetric]
                        record["sensorValue"] = switchSimulatorSeedMap[cmc][switchGUID][ibmetric]
                        record["timestamp"] = timestamp
                        record["deviceUuid"] = device_uuid[cmc][switchGUID]
                        record["sensorName"] = ibmetric
                        record["deviceId"] = switchGUID
                        #print(record)
                        record_list.append(record)

                    for eachRecord in record_list:
                        #print(str(eachRecord))
                        if self.myAgent_debug == True:
                            print(str(i) + ":Publishing via mqtt (topic:%s)" % self.myAgent_send_ts_data_topic)
                        
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
        self.myDeviceMap = self.create_my_device_map()
        self.mqtt_device_registration(self.myDevice_registration_request_topic, self.myDevice_registration_response_topic, self.myDeviceMap)
        
        # start sending data
        self.send_data()


# END IBswitchSimulator class
################################################################################


def main():
    
    usage = "usage: %s --mode=mqtt" % sys.argv[0]
    parser = OptionParser(usage=usage, version=__version__)

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
        help="logger level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    (options, _) = parser.parse_args()

    option_dict = vars(options)

    # load container config
    myIBswitchSimulator = IBswitchSimulator("IBswitchSimulator.cfg", debug=option_dict["debug"])
    signal.signal(signal.SIGINT, myIBswitchSimulator.signal_handler)
    myIBswitchSimulator.run()


if __name__ == "__main__":
    main()
