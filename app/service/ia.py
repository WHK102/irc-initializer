#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


class IaService(object):

    def __init__(self, config):

        self.config = config


    def createInstance(self, ircClient):

        self.client = ircClient

        # Handle events
        self.client.setOnConnect(self.onConnect)
        self.client.setOnReceivePrivateMessage(self.onReceivePrivateMessage)
        self.client.setOnReceiveChannelMessage(self.onReceiveChannelMessage)


    def onConnect(self):

        # Login in
        self.client.sendCommand(b'NICK', self.config['nick'])
        self.client.sendCommand(b'USER', self.config['nick'] + b'  8 x : ' + self.config['nick'])
        # self.client.sendCommand(b'JOIN', '#underc0de')


    def onReceivePrivateMessage(self, user, message):

        matches = re.search(
            br'^(test)$',
            message
        )

        self.client.sendPrivateMessage(
            toNick=user['nick'],
            message=(b'Hola %s, esta es una prueba de respuesta a tu mensaje.' % (user['nick'],))
        )
        

    def onReceiveChannelMessage(self, channel, user, message):
        
        pass
