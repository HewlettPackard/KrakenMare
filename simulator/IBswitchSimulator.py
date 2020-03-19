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
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import MessageSerializer

# project imports
from version import __version__
from agentcommon import AgentCommon

# START IBswitchSimulator class


class IBswitchSimulator(AgentCommon):
    myMQTTregistered = False
    myMQTTderegistered = False
    loggerName = None

    def __init__(self, configFile, debug, encrypt, numberOfTopics, batching=False):
        """
            Class init
        """

        self.loggerName = "simulator.agent." + __version__ + ".log"

        # AgentCommon class method
        self.config = self.checkConfigurationFile(configFile, ["Others"])

        self.myAgentName = "IBSwitchSimulator"
        self.myAgent_debug = debug
        self.MQTTbatching = batching

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
        self.sendNumberOfMessages = self.config.get("Others", "sendNumberOfMessages")

        if self.sendNumberOfMessages == "":
            self.sendNumberOfMessages = -1
        else:
            self.sendNumberOfMessages = int(self.sendNumberOfMessages)

        self.myDeviceMap = {}

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

        # topic will have added /# depending on number of subtopics, without subtopics this translates to: ibswitch/0 as standard topic
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

        super().__init__(configFile, debug)

        self.setMqttNumberOfPublishingTopics(int(numberOfTopics))

    # defines self.myMQTTregistered and self.myAgent_uuid
    def mqtt_on_message(self, client, userdata, message):
        print("on_message: message received on topic: %s" % message.topic)

        # since we transmit topic lists, this one has only one entry, and in this entry the first item is the topic name
        if message.topic == self.myAgent_registration_response_topic[0][0]:
            print("message: %s " % message.payload)
            data = self.msg_serializer.decode_message(message.payload)
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
            print("message: %s " % message.payload)
            data = self.msg_serializer.decode_message(message.payload)
            self.myDeviceRegistered = True
            print("Devices registered")

        # since we transmit topic lists, this one has only one entry, and in this entry the first item is the topic name
        elif message.topic == self.myAgent_deregistration_response_topic[0][0]:
            self.myMQTTderegistered = True
            print("message: %s " % message.payload)
            data = self.msg_serializer.decode_message(message.payload)
            print(str(data))

        else:
            print(
                "Unknown topic: "
                + str(message.topic)
                + " -- message received: %s " % message.payload
            )

    ################################################################################
    # create my device and sensor map
    def create_my_device_map(self):

        # store for final device and sensor map according to InfinibandAgent.json syntax
        deviceMap = {}

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
                # read device json template to reset it
                with open(self.device_json_dir + "/InfinibandDevice.json", "r") as f:
                    deviceTemplate = json.load(f)

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
                seedMap[cmc][guid]["Name"] = (
                    self.myAgentName + ":" + str(self.myAgent_uid)
                )

        # done
        return seedMap

    # assemble and send simulated sensor data via MQTT (overwrites example method in parent class)

    def send_data(self):

        # counter for send message count
        i = 0

        # Create a dictionary of the 18 IB metrics names
        ibmetrics = ["SymbolErrorCounter", "PortXmitData"]

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
            "timestamp": 1570135369000,
            "sensorUuid": "afbfa80d-cd9d-487a-841c-6da12b10c6d0",
            "sensorValue": 0.0,
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

                # device UUID
                device_uuid[cmc][switch_guid] = uuid.UUID(
                    hashlib.md5(
                        (str(self.myAgent_uuid) + switch_guid).encode()
                    ).hexdigest()
                )

                sensor_uuid[cmc][switch_guid] = {}

                for ibmetric in ibmetrics:

                    # sensor UUIID
                    sensor_uuid[cmc][switch_guid][ibmetric] = uuid.UUID(
                        hashlib.md5(
                            (
                                str(self.myAgent_uuid)
                                + str(device_uuid[cmc][switch_guid])
                                + ibmetric
                            ).encode()
                        ).hexdigest()
                    )
                    if ibmetric in ["SymbolErrorCounter", "PortXmitData"]:
                        print(
                            ibmetric
                            + ":"
                            + str(sensor_uuid[cmc][switch_guid][ibmetric])
                        )

        switchSimulatorSeedMap = self.seed_simulator_map()

        # baremetal nodes have python 3.6 hence we don't have time_ns. Here time is a floating point number
        self.timet0 = time.time()
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
                        switchSimulatorSeedMap[cmc][switchGUID][
                            "SymbolErrorCounter"
                        ] += 1000
                    elif x > 0.88:
                        switchSimulatorSeedMap[cmc][switchGUID][
                            "SymbolErrorCounter"
                        ] += 10
                    elif x > 0.78:
                        switchSimulatorSeedMap[cmc][switchGUID][
                            "SymbolErrorCounter"
                        ] += 1

                    x = random.random()
                    if x > 0.99:
                        switchSimulatorSeedMap[cmc][switchGUID][
                            "LinkDownedCounter"
                        ] += 100
                    elif x > 0.89:
                        switchSimulatorSeedMap[cmc][switchGUID][
                            "LinkDownedCounter"
                        ] += 5
                    elif x > 0.79:
                        switchSimulatorSeedMap[cmc][switchGUID][
                            "LinkDownedCounter"
                        ] += 1

                    x = random.random()
                    if x > 0.99:
                        switchSimulatorSeedMap[cmc][switchGUID][
                            "PortXmitDiscards"
                        ] += 10
                    elif x > 0.89:
                        switchSimulatorSeedMap[cmc][switchGUID]["PortXmitDiscards"] += 5
                    elif x > 0.79:
                        switchSimulatorSeedMap[cmc][switchGUID]["PortXmitDiscards"] += 2

                    # Assign the simulator values to the record to be serialized
                    for ibmetric in ibmetrics:
                        record = {}
                        record["timestamp"] = timestamp
                        record["sensorUuid"] = sensor_uuid[cmc][switchGUID][ibmetric]
                        record["sensorValue"] = switchSimulatorSeedMap[cmc][switchGUID][
                            ibmetric
                        ]
                        # print(record)
                        record_list.append(record)

                    self.mqtt_send_triplet_batch(
                        self.myAgent_send_ts_data_topic,
                        record_list,
                        self.sendNumberOfMessages,
                        self.batch_size,
                        self.myAgent_uuid,
                        self.timet0,
                    )

            # Infinite loop
            time.sleep(self.sleepLoopTime)

    def signal_handler(self, signal, frame):
        self.mqtt_close()
        sys.exit(0)

    # main method of IBswitchSimulator
    def run(self):

        # start mqtt client
        myLoopForever = False
        myCleanSession = False
        self.mqtt_init(
            self.myAgent_uid,
            self.myAgent_registration_response_topic,
            myLoopForever,
            myCleanSession,
            self.myAgent_mqtt_encryption_enabled,
        )

        # register myself
        self.mqtt_registration(
            self.myAgent_registration_request_topic[0], self.myRegistrationData
        )
        
        # register my devices/sensors
        self.myDeviceMap = self.create_my_device_map()
        self.mqtt_device_registration(
            self.myDevice_registration_request_topic,
            self.myDevice_registration_response_topic,
            self.myDeviceMap,
        )
        
        # start sending data
        # self.send_data()
        time.sleep(10)
        self.mqtt_deregistration(self.myAgent_deregistration_request_topic[0], self.myAgent_uuid)


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
        "--numberOfTopic",
        dest="numberOfTopic",
        default=False,
        help="specify this option in order to publish to multiple topics (# of topics (need to be able to divide 16 by this,e.g. --numberOfTopic=2), defaults to 1",
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
    myIBswitchSimulator = IBswitchSimulator(
        "IBswitchSimulator.cfg",
        debug=option_dict["debug"],
        encrypt=option_dict["encrypt"],
        numberOfTopics=numberOfMqttTopics,
        batching=option_dict["batching"],
    )
    signal.signal(signal.SIGINT, myIBswitchSimulator.signal_handler)
    myIBswitchSimulator.run()


if __name__ == "__main__":
    main()
