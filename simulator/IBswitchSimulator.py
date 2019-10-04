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

# avro imports
import avro.schema  # pip3 install avro-python3
import avro.io  # pip3 install avro-python3
import avro.datafile  # pip3 install avro-python3
import io

# project imports
from version import __version__
from schema_registry.client import SchemaRegistryClient

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

        self.mqtt_broker = self.config.get("MQTT", "mqtt_broker")
        self.mqtt_port = int(self.config.get("MQTT", "mqtt_port"))
        self.sleepLoopTime = float(self.config.get("Others", "sleepLoopTime"))
        self.seedOutputDir = self.config.get("Others", "seedOutputDir")

        # id comes from the framework manager as a convenience incremental id
        self.myAgent_id = -1
        # uuid comes from the central framework manager
        self.myAgent_uuid = -1
        self.myAgentName = "IBSwitchSimulator"
        self.data_topic = "ibswitch"
        self.myMQTTregistered = False
        # Agent uid as provided by the discovery mecanism.
        # for now use the hostname, should be the output of the disc mecanism
        self.myAgent_uid = platform.node()

        conf = {
            "url": "https://schemaregistry:8081",
            "ssl.ca.location": "/run/secrets/km-ca-1.crt",
            "ssl.certificate.location":
            "/run/secrets/schemaregistry.certificate.pem",
            "ssl.key.location": "/run/secrets/schemaregistry.key",
        }

        client = SchemaRegistryClient(conf)
        subject = "com-hpe-krakenmare-message-agent-register-request"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)

        register_request_schema = cg.schema

        # two ugly things
        # ' --> '' and True --> true to have proper avro-parsable JSON
        # tbd fix me
        mystring = str(register_request_schema)
        buffer = mystring.replace("'", '"')
        self.schema_register_request = avro.schema.Parse(
            buffer.replace("True", "true"))

        subject = "com-hpe-krakenmare-message-manager-register-response"
        cg = None
        while cg is None:
            cg = client.get_schema(subject)
            print("getting schema %s from schemaregistry" % subject)
            time.sleep(1)

        register_response_schema = client.get_schema(subject).schema
        mystring = str(register_response_schema)
        buffer = mystring.replace("'", '"')
        self.schema_register_response = avro.schema.Parse(
            buffer.replace("True", "true")
        )

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

    # MQTT agent methods
    def mqtt_on_log(self, client, userdata, level, buf):

        print("log: %s" % buf)

    # TODO: for now we listen to any response, not only ours
    # defines self.myMQTTregistered and self.myAgent_id
    def mqtt_on_registration_result(self, client, userdata, message):

        print("message received: %s " % message.payload)
        print("message topic: %s" % message.topic)
        reader = avro.io.DatumReader(self.schema_register_response)
        bytes_reader = io.BytesIO(message.payload)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        data = reader.read(decoder)
        print("registration-result with km UUID: %s" % data["uuid"])
        self.myMQTTregistered = True
        self.myAgent_uuid = data["uuid"]

    def mqtt_registration(self):
        registration_client = mqtt.Client("RegistrationClient")
        registration_client.on_log = self.mqtt_on_log
        registration_client.on_message = self.mqtt_on_registration_result
        print("connecting to mqtt broker:" + self.mqtt_broker)
        registration_client.connect(self.mqtt_broker)
        registration_client.loop_start()

        registration_client.subscribe(
            "registration/" + self.myAgent_uid + "/response")

        writer = avro.io.DatumWriter(self.schema_register_request)
        RegistrationData = {
            "agentID": self.myAgent_uid,
            "type": "simulatorAgent",
            "name": "IBswitchSimulator",
            "description": "This is a fine description",
            "useSensorTemplate": False,
        }

        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(RegistrationData, encoder)
        raw_bytes = bytes_writer.getvalue()

        # use highest QoS for now
        print("sending registration payload: --%s--" % raw_bytes)
        registration_client.publish(
            "registration/" + self.myAgent_uid + "/request", raw_bytes, 2, True
        )

        while not self.myMQTTregistered:
            time.sleep(1)
            print("waiting for registration result...")

        registration_client.loop_stop()
        print(
            "registered with uid '%s' and km-uuid '%s'"
            % (self.myAgent_uid, self.myAgent_uuid)
        )

    # END MQTT agent methods

    # send simulated sensor data via MQTT
    def send_data(self, pubsubType):

        if pubsubType == "mqtt":
            client = mqtt.Client("DataClient")
            print("connecting to mqtt broker")
            client.connect(self.mqtt_broker, self.mqtt_port)
        else:
            print("Unknown Pub/Sub type selected: " + pubsubType)
            sys.exit(-1)

        # Infinite loop
        while True:

            # fresh output map
            query_output_new = {}

            # read JSON data describing switches in the IRU (c stands for CMC)
            for cmc in ["r1i0c-ibswitch", "r1i1c-ibswitch"]:
                with open(cmc, "r") as f:
                    query_data = json.load(f)

                # For each switch found in the JSON data ,
                # generate perfquery with -a to summarize the ports
                # This simulates a poor quality fabric in heavy use
                # Using random numbers on 0,1 we update 3 error counters as
                # SymbolErrorCounter increments fastest
                # LinkedDownedCounter increments slower both fewer and less
                # PortXmitDiscards increments slowest both fewer and less
                # For data counters add randint[1000,4000]
                # for packet counters add randint[100,400]

                # Set time to milliseconds since the epoch for InfluxDB
                nowint = int(round(time.time() * 1000))

                # set timestamp
                timestamp = nowint

                # create empty map for timestamp to store sensorID:value pairs
                query_output_new[str(timestamp)] = {}

                # go through sensors for device
                for switch in query_data["Switch"]:
                    guid = str(switch["Node_GUID"])
                    # Read in the old query output
                    output = self.seedOutputDir + \
                        "/" + guid + ".perfquery.json"
                    with open(output, "r") as g:
                        query_output = json.load(g)
                    g.close()

                    # set sensor ID prefix
                    # TODO: fix id's after registration works
                    sensorIdPrefix = "tw-" + self.myAgentName + "-" + guid

                    # TODO: remove old query_output
                    query_output["Name"] = self.myAgentName
                    query_output["Timestamp"] = nowint
                    x = random.random()
                    if x > 0.98:
                        query_output["SymbolErrorCounter"] += 1000
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-SymbolErrorCounter")
                        ] = query_output["SymbolErrorCounter"]
                    elif x > 0.88:
                        query_output["SymbolErrorCounter"] += 10
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-SymbolErrorCounter")
                        ] = query_output["SymbolErrorCounter"]
                    elif x > 0.78:
                        query_output["SymbolErrorCounter"] += 1
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-SymbolErrorCounter")
                        ] = query_output["SymbolErrorCounter"]
                    else:
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-SymbolErrorCounter")
                        ] = query_output["SymbolErrorCounter"]

                    x = random.random()
                    if x > 0.99:
                        query_output["LinkDownedCounter"] += 100
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-LinkDownedCounter")
                        ] = query_output["LinkDownedCounter"]
                    elif x > 0.89:
                        query_output["LinkDownedCounter"] += 5
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-LinkDownedCounter")
                        ] = query_output["LinkDownedCounter"]
                    elif x > 0.79:
                        query_output["LinkDownedCounter"] += 1
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-LinkDownedCounter")
                        ] = query_output["LinkDownedCounter"]
                    else:
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-LinkDownedCounter")
                        ] = query_output["LinkDownedCounter"]

                    x = random.random()
                    if x > 0.99:
                        query_output["PortXmitDiscards"] += 10
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-PortXmitDiscards")
                        ] = query_output["PortXmitDiscards"]
                    elif x > 0.89:
                        query_output["PortXmitDiscards"] += 5
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-PortXmitDiscards")
                        ] = query_output["PortXmitDiscards"]
                    elif x > 0.79:
                        query_output["PortXmitDiscards"] += 2
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-PortXmitDiscards")
                        ] = query_output["PortXmitDiscards"]
                    else:
                        query_output_new[str(timestamp)][
                            str(sensorIdPrefix + "-PortXmitDiscards")
                        ] = query_output["PortXmitDiscards"]

                    query_output["PortXmitData"] += random.randint(1000, 4000)
                    query_output_new[str(timestamp)][
                        str(sensorIdPrefix + "-PortXmitData")
                    ] = query_output["PortXmitData"]
                    query_output["PortRcvData"] += random.randint(1000, 4000)
                    query_output_new[str(timestamp)][
                        str(sensorIdPrefix + "-PortRcvData")
                    ] = query_output["PortRcvData"]
                    query_output["PortXmitPkts"] += random.randint(100, 400)
                    query_output_new[str(timestamp)][
                        str(sensorIdPrefix + "-PortXmitPkts")
                    ] = query_output["PortXmitPkts"]
                    query_output["PortRcvPkts"] += random.randint(100, 400)
                    query_output_new[str(timestamp)][
                        str(sensorIdPrefix + "-PortRcvPkts")
                    ] = query_output["PortRcvPkts"]
                    query_output["PortXmitWait"] += random.randint(100, 200)
                    query_output_new[str(timestamp)][
                        str(sensorIdPrefix + "-PortXmitWait")
                    ] = query_output["PortXmitWait"]

                    # Write output to the next input
                    with open(output, "w") as g:
                        json.dump(query_output, g)
                    g.close()

            data_out_new = json.dumps(query_output_new).encode("utf-8")

            if pubsubType == "mqtt":
                print("Publishing via mqtt (topic:%s)" % self.data_topic)
                client.publish(self.data_topic, data_out_new)
            else:
                print("error: shouldn't be here")
                sys.exit(-1)

            # Infinite loop
            time.sleep(self.sleepLoopTime)

    # main method of IBswitchSimulator
    def run(self, mode, local, debug):
        # local and debug flag are not used from here at the moment

        if mode == "mqtt":
            print("mqtt mode")
            self.mqtt_registration()
            self.send_data("mqtt")


# END IBswitchSimulator class


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
