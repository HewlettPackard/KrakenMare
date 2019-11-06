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
from optparse import OptionParser
from fastavro import schemaless_writer, schemaless_reader

import io
import uuid
import hashlib

# project imports
from version import __version__

from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import MessageSerializer


# START IBswitchSimulator class
class IBswitchSimulator:
    registered = False
    loggerName = None

    def __init__(self, configFile, mode):
        """
            Class init
            
        """

        self.loggerName = "simulator.agent." + __version__ + ".log"

        self.config = self.checkConfigurationFile(
            configFile, ["Daemon", "Logger", "MQTT"]
        )

        self.myAgentName = "IBSwitchSimulator"
        
        # Agent uid as provided by the discovery mechanism.
        # for now use the hostname and random number to insure we are always unique
        # used for Agent registration and MQTT client id
        self.myAgent_uid = platform.node() + str(random.randint(1, 100001))
        
        # uuid comes from the central framework manager
        self.myAgent_uuid = -1

        self.sleepLoopTime = float(self.config.get("Others", "sleepLoopTime"))
        self.seedOutputDir = self.config.get("Others", "seedOutputDir")
        self.device_json_dir = self.config.get("Others", "deviceJSONdir")
        self.myDeviceMap = {}
        
        # MQTT setup
        self.mqtt_broker = self.config.get("MQTT", "mqtt_broker")
        self.mqtt_port = int(self.config.get("MQTT", "mqtt_port"))
        self.data_topic = "ibswitch"
        self.myMQTTregistered = False
        self.myDeviceRegistered = False
        self.myAgent_registration_response_topic = "registration/" + self.myAgent_uid + "/response"
        self.myAgent_registration_request_topic = "registration/" + self.myAgent_uid + "/request"
        self.myDevice_registration_response_topic = False
        self.myDevice_registration_request_topic = "device-registration/"
        
        # schemas and schema registry setup
        conf = {
            "url": "https://schemaregistry:8081",
            "ssl.ca.location": "/run/secrets/km-ca-1.crt",
            "ssl.certificate.location": "/run/secrets/schemaregistry.certificate.pem",
            "ssl.key.location": "/run/secrets/schemaregistry.key",
        }

        client = SchemaRegistryClient(conf)
        self.msg_serializer = MessageSerializer(client)
        
        subject = "com-hpe-krakenmare-message-agent-register-request"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(5)
        self.agent_register_request_schema = cg.schema.schema
        self.agent_register_request_schema_id = cg.schema_id

        subject = "com-hpe-krakenmare-message-manager-register-response"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(5)
        self.agent_register_response_schema = cg.schema.schema
        self.agent_register_response_schema_id = cg.schema_id

        subject = "com-hpe-krakenmare-message-agent-send-time-series-druid"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(5)
        self.send_time_series_schema = cg.schema.schema
        self.send_time_series_schema_id = cg.schema_id
        
        subject = "com-hpe-krakenmare-message-agent-device-list"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(5)
        self.device_register_request_schema = cg.schema.schema
        self.device_register_request_schema_id = cg.schema_id
        
        subject = "com-hpe-krakenmare-message-manager-device-list-response"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(5)
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
        print("on_log: %s" % buf)

    def mqtt_on_subscribe(self, client, userdata, mid, granted_qos):
        print("on_subscribe: Subscribed with message id (mid): " + str(mid))
        
    # The callback for when the client receives a CONNACK response from the server.
    def mqtt_on_connect(self, client, userdata, flags, rc):
        
        if (rc != 0):
            print("on_connect: Connection error: " + mqtt.connack_string(rc))
        else:
            print("on_connect: Connected with result code: " + mqtt.connack_string(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        if self.myAgent_registration_response_topic != False:
            self.registration_client.subscribe(self.myAgent_registration_response_topic)
        
        if self.myDevice_registration_response_topic != False:
            self.registration_client.subscribe(self.myDevice_registration_response_topic)

    def mqtt_on_disconnect(self, client, userdata, rc):
        print("on_disconnect: DisConnected result code: " + mqtt.connack_string(rc))
    
    def mqtt_on_publish(self, client, userdata, mid):
        print("on_publish: Published message with mid: " + str(mid))

    # defines self.myMQTTregistered and self.myAgent_uuid
    def mqtt_on_message(self, client, userdata, message):
        print("on_message: message received on topic: %s" % message.topic)
        
        if message.topic == self.myAgent_registration_response_topic:
            print("message received: %s " % message.payload)
            # TO-DO, decoding with schema-registry requires magic byte in message
            #decode_msg_obj = self.msg_serializer.decode_message(message.payload)
            #print("registration-result with km UUID: %s" % decode_msg_obj["uuid"])
            
            r_bytes = io.BytesIO(message.payload)
            data = schemaless_reader(r_bytes, self.agent_register_response_schema)
            print("registration-result with KrakenMare UUID: %s" % data["uuid"])
            self.myMQTTregistered = True
            self.myAgent_uuid = data["uuid"]
            self.myDevice_registration_response_topic = "device-registration/" + str(self.myAgent_uuid)
        
        if message.topic == self.myDevice_registration_response_topic:
            print("message received: %s " % message.payload)
            r_bytes = io.BytesIO(message.payload)
            data = schemaless_reader(r_bytes, self.device_register_response_schema)
            self.myDeviceRegistered = True
            
    # this method takes care of Agent registration and device/sensor registration
    def mqtt_registration(self):
        self.registration_client = mqtt.Client("RegistrationClient-" + str(self.myAgent_uid))
        self.registration_client.on_log = self.mqtt_on_log
        self.registration_client.on_message = self.mqtt_on_message
        self.registration_client.on_subscribe = self.mqtt_on_subscribe
        self.registration_client.on_disconnect = self.mqtt_on_disconnect
        self.registration_client.on_connect = self.mqtt_on_connect
        self.registration_client.on_publish = self.mqtt_on_publish
        print("connecting to mqtt broker:" + self.mqtt_broker)
        self.registration_client.connect(self.mqtt_broker)
        
        # start listening loop
        self.registration_client.loop_start()

        # subscribe to registration response topic
        result = -1
        while result != mqtt.MQTT_ERR_SUCCESS:
            (result, mid) = self.registration_client.subscribe(self.myAgent_registration_response_topic)      
        
        # assemble my agent registration data
        RegistrationData = {
            "agentId": self.myAgent_uid,
            "type": "simulatorAgent",
            "agentName": "IBswitchSimulator",
            "description": "This is a fine description",
            "useSensorTemplate": False,
        }
        
        # publish registration data
        w_bytes = io.BytesIO()

        schemaless_writer(
            w_bytes, self.agent_register_request_schema, RegistrationData)

        raw_bytes = w_bytes.getvalue()

        # TO-DO: change to magic byte in Avro message on FM site
        #raw_bytes = self.msg_serializer.encode_record_with_schema_id(self.agent_register_request_schema_id, RegistrationData)

        # use highest QoS for now
        print("sending registration payload: --%s--" % raw_bytes)
        MQTTMessageInfo = self.registration_client.publish(self.myAgent_registration_request_topic, raw_bytes, 2, True)
        print("mqtt published with publishing code: " + mqtt.connack_string(MQTTMessageInfo.rc))
        if MQTTMessageInfo.is_published() == False:
            print("Waiting for message to be published.")
            MQTTMessageInfo.wait_for_publish()
            
        #self.registration_client.publish("registration/" + self.myAgent_uid + "/request", raw_bytes, 2, True)

        while not self.myMQTTregistered:
            print("waiting for agent registration result...")
            time.sleep(5)
            '''
            if not self.myMQTTregistered:
                print("re-sending registration payload")
                self.registration_client.publish(self.myAgent_registration_request_topic, raw_bytes, 2, True)
            '''
        
        '''
        # subscribe to registration response topic
        result = -1
        while result != mqtt.MQTT_ERR_SUCCESS:
            (result, mid) = self.registration_client.subscribe(self.myDevice_registration_response_topic)   
        
        # register devices/sensors
        self.myDeviceMap = self.create_my_device_map()
        
        #print(self.myDeviceMap)
        
        # publish registration data
        w_bytes = io.BytesIO()

        schemaless_writer(
            w_bytes, self.device_register_request_schema, self.myDeviceMap)

        raw_bytes = w_bytes.getvalue()
        
        # use highest QoS for now
        print("sending device/sensor registration payload: --%s--" % raw_bytes)
        self.registration_client.publish(self.myDevice_registration_request_topic, raw_bytes, 2, True)
        #self.registration_client.publish("registration/" + self.myAgent_uid + "/request", raw_bytes, 2, True)

        while not self.myDeviceRegistered:
            print("waiting for device registration result...")
            time.sleep(10)
            if not self.myDeviceRegistered:
                print("re-sending device/sensor registration payload")
                self.registration_client.publish(self.myDevice_registration_request_topic, raw_bytes, 2, True)
        '''

        self.registration_client.loop_stop()
        print(
            "registered with uid '%s' and km-uuid '%s'"
            % (self.myAgent_uid, self.myAgent_uuid)
        )

    # END MQTT agent methods
    ################################################################################

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
        # go through high level devices and add each switch as device (deviceUID = myAgentUUID + device guid
        for cmc in ["r1i0c-ibswitch", "r1i1c-ibswitch"]:
            
            with open(cmc, "r") as f:
                query_data = json.load(f)

            # For each switch found in the JSON data ,
            # assemble map for each device and store it in myDeviceMap
            for switch in query_data["Switch"]:
                deviceTemplate["deviceID"] = 'null'
                deviceTemplate["deviceID"] = switch["Node_GUID"]
                deviceTemplate["deviceName"] = "use CMC or node with -ib postfix"
                deviceTemplate["type"] = "Infiniband Switch or Infiniband HCA"
                deviceTemplate["location"] = "use CMC or node"
                
                # assemble sensor information for device 'switch'
                for sensor in deviceTemplate["sensors"]:
                    sensor["sensorUUID"] = 'null'
                    # sensorID = guid-sensorname
                    sensor["sensorID"] = switch["Node_GUID"] + "-" + sensor["sensorName"]          
                
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
        
    
    # assemble and send simulated sensor data via MQTT
    def send_data(self, pubsubType):
               
        # counter for send message count
        i = 1

        if pubsubType == "mqtt":
            client = mqtt.Client(self.myAgent_uid)
            print("connecting to mqtt broker")
            client.connect(self.mqtt_broker, self.mqtt_port)
        else:
            print("Unknown Pub/Sub type selected: " + pubsubType)
            sys.exit(-1)

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

                    if pubsubType == "mqtt":
                        for eachRecord in record_list:
                            #print(str(eachRecord))
                            print(str(i) + ":Publishing via mqtt (topic:%s)" % self.data_topic)
                            
                            raw_bytes = self.msg_serializer.encode_record_with_schema_id(self.send_time_series_schema_id, eachRecord)
                            client.publish(self.data_topic, raw_bytes)
                            i += 1
                    else:
                        print("error: shouldn't be here")
                        sys.exit(-1)

            # Infinite loop
            seed_initilaized = True
            time.sleep(self.sleepLoopTime)

    # main method of IBswitchSimulator
    def run(self, mode, local, debug):
        # local and debug flag are not used from here at the moment

        if mode == "mqtt":
            print("mqtt mode")
            self.mqtt_registration()
            self.send_data("mqtt")


# END IBswitchSimulator class
################################################################################

def main():
    usage = "usage: %s --mode=mqtt" % sys.argv[0]
    parser = OptionParser(usage=usage, version=__version__)

    parser.add_option("--mode", dest="modename", help="specify mode: mqtt")
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
        help="logger level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    (options, _) = parser.parse_args()

    option_dict = vars(options)

    if option_dict["modename"] is None:
        print("Incorrect usage")
        parser.print_help()
        sys.exit(0)

    if options.local is True:
        # load development config to run outside of container
        myIBswitchSimulator = IBswitchSimulator(
            "IBswitchSimulator_dev.cfg", "local")
    else:
        # load container config
        myIBswitchSimulator = IBswitchSimulator(
            "IBswitchSimulator.cfg", "container")

    if options.modename == "mqtt":
        myIBswitchSimulator.run(
            "mqtt", local=option_dict["local"], debug=option_dict["debug"]
        )

    else:
        print("ERROR: Unknown action command.")
        sys.exit(2)


if __name__ == "__main__":
    main()
