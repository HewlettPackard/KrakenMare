#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Licensed under the Apache v2 license
# Copyright Hewlett-Packard Enterprise, 2019

import sys
from datetime import datetime
import hashlib

class KrakenMareTriplet(object):
    """
        This class defines KrakenMare triplet which is use to exchange data between agents and fanin
    """

    def __init__(self, idx):
        self.timestamp = int(round(datetime.timestamp(datetime.now())*1000))
        self.idx = idx
    
    def set_uuid(self, topic):
        self.uuid = hashlib.md5(topic.encode()).hexdigest()
        self.key = topic

    def set_value(self, value):
        # The key will serve as a way to recover the MQTT/Kafka topic on the other end of the pipe
        # through a registration to a registry
        self.value = value

    def register(self, registry):
        # This method needs to be called in order to keep track of the link between the uuid and the key
        #register-agent(self.key,self.uuid)
        pass

    def print(self):
        print('[' + str(self.idx) + ']: Publishing triplet: timestamp: ' + str(self.timestamp) + ', uuid: ' + self.uuid + ', value: ' + str(self.value))

if __name__ == '__main__':
    pass
    
