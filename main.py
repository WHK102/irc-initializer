#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse
import time

from modules.client import Client
from modules.ia     import Ia


class MainCls:

    def __init__(self):
        self.x = None
        self.config = None
        self.client = Client()
        self.ia     = Ia()

        # Procesador de argumentos
        argparseHandler = argparse.ArgumentParser(
            add_help=False
        )

        argparseHandler.add_argument(
            '-h',
            '--help',
            dest='help',
            action='store_true'
        )
        argparseHandler.add_argument(
            '-c',
            '--config',
            dest='config',
            nargs='?'
        )

        # Procesa los argumentos a partir de los argumentos obtenidos por sys
        argparseParsed, argparseUnknown = argparseHandler.parse_known_args(
            sys.argv[1:]
        )

        # Hay argumentos?
        if(argparseParsed.help):
            # Muestra el mensaje de ayuda
            return self.help()

        if(argparseParsed.config):

            # El archivo de configuración existe?
            if(not os.path.isfile(argparseParsed.config)):
                return print('! El archivo de configuración no existe: ' + argparseParsed.config)

            # Carga las configuraciones
            self.config = json.load(open(argparseParsed.config))

        else:
            defaultPath = os.path.dirname(os.path.abspath(__file__)) + '/config.json'

            # Existe el archivo de configuración por defecto?
            if(not os.path.isfile(defaultPath)):
                return print('! El archivo de configuración no existe: ' + defaultPath)

            # Carga las configuraciones desde la localización por defecto
            self.config = json.load(open(defaultPath))

        # Eventos
        self.client.onConnecting            = self.onConnecting
        self.client.onConnect               = self.onConnect
        self.client.onDisconnect            = self.onDisconnect
        self.client.onSendCommand           = self.onSendCommand
        self.client.onReceive               = self.onReceive
        self.client.onReceivePrivateMessage = self.onReceivePrivateMessage

        # Conecta y deja que fluya a traves de los eventos ...
        self.client.connect(
            host=str(self.config['server']['host']),
            port=int(self.config['server']['port'])
        )


    def help(self):

        print('\n'.join([
            '-h, --help            Muestra el mensaje de ayuda.',
            '-c, --config [path]   Carga el archivo de configuración específico,',
            '                      en caso contrario utilizará el archivo config.json',
            '                      localizado en la raiz del script.'
        ]))


    def onConnecting(self, host, port):

        print('+ Conectando a %s:%d ...' % (host, port))


    def onConnect(self, host, port):

        print('+ Conectado!')


    def onDisconnect(self):

        print('+ Disconnected.')


    def onSendCommand(self, command, arguments):

        print('-> %s %s' % (command, arguments))


    def onReceive(self, rawLine, response):

        print('<- %s' % (rawLine,))
        # print('<- %s' % (str(response),))

        if(self.x is None):
            self.x = 1
            self.client.setNick(self.config['nick'])


    def onReceivePrivateMessage(self, user, message):

#        print(
#            '%s -> %s: %s' % (
#                user['nick'].decode(),
#                self.config['nick'],
#                message
#            )
#        )

        # Envía el mensaje al procesador de mensajes
        self.ia.receiveMessage(user, message)
        self.client.joinChannel('#underc0de')



if __name__ == '__main__':
    mainCls = MainCls()
