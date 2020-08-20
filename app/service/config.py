#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json


class ConfigService(object):


    def __init__(self):

        pass


    def getFromFile(self, path):

        # Handle exceptions (file not found & json parser)
        config = json.load(open(path))

        # Transform values
        config['nick'] = config['nick'].encode(
            encoding='ISO-8859-1',
            errors='ignore'
        )

        # Return the dict
        return config