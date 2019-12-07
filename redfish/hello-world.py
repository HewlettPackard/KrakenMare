#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Licensed under the APache v2 license
# Copyright Hewlett-Packard Enterprise, 2019

import os
import sys
import io
import redfish
import time
from KrakenMareTriplet import KrakenMareTriplet

# Time to wait between requests
SLEEP = 120

machine = str(os.environ['REDFISHIP'])
topicroot = "redfish/" + machine.split("://")[1].split("/")[0] + '/'

# Infinite loop
i = 0
while True:
    i = i + 1
    km = KrakenMareTriplet(i)
    if os.environ['REDFISHACC'] == "":
        simulator = True
        enforceSSL = False
    else:
        simulator = False
        enforceSSL = True
    try:
        redfish_data = redfish.connect(os.environ['REDFISHIP'],
                                    os.environ['REDFISHACC'],
                                    os.environ['REDFISHPWD'],
                                    verify_cert=False,
                                    simulator=simulator,
                                    enforceSSL=enforceSSL)
    except redfish.exception.RedfishException as e:
            sys.stderr.write(str(e.message))
            sys.stderr.write(str(e.advices))
            print("Sleeping " + str(SLEEP) + " seconds")
            time.sleep(SLEEP)
            continue

    for chassis in redfish_data.Chassis.chassis_dict.values():
        name = chassis.get_name()
        for sensor, temp in chassis.thermal.get_temperatures().items():
            # Using https://docs.python.org/3/library/uuid.html
            s = topicroot + '-' + name + '-' + sensor

            # Interface with KrakenMareTriplet
            km.set_uuid(s)
            km.set_value(float(temp))
            km.print()

        for fan, rpm in chassis.thermal.get_fans().items():
            rpml = rpm.split(None, 1)
            rpm = rpml[0]
            s = topicroot + '-' + name + '-' + fan

            # Interface with KrakenMareTriplet
            km.set_uuid(s)
            km.set_value(float(rpm))
            km.print()

    # Infinite loop - Redfish is slow so wait
    print("Sleeping " + str(SLEEP) + " seconds")
    time.sleep(SLEEP)
