#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.service.irc import IrcService
from app.service.ia  import IaService


class MainController(object):

    def __init__(self, config):

        ircService = IrcService()
        iaService = IaService(config)

        client = ircService.createClient(
            host=str(config['server']['host']),
            port=int(config['server']['port'])
        )

        iaInstance = iaService.createInstance(client)

        # Events
        client.setOnConnecting(lambda:{
                print('+ Connecting to %s:%s ...' % (
                    str(config['server']['host']),
                    str(config['server']['port'])
                ))

            }).setOnConnect(lambda:
                print('+ Connected!')

            ).setOnDisconnect(lambda:{
                print('+ Disconnected!')

            }).setOnSendCommand(lambda command, arguments:{
                print('-> %s %s' % (command, arguments))

            }).setOnRawReceive(lambda rawLine:{
                print('<- . %s' % (rawLine,))

            }).setOnReceive(lambda response:{
                print('<- .. %s' % (response,))

            }).setOnReceivePrivateMessage(lambda user, message:{
                print(
                    '%s <- %s: %s' % (
                        user['nick'].decode(),
                        config['nick'],
                        message
                    )
                )
                
            }).setOnReceiveChannelMessage(lambda channel, user, message:{
                print(
                    '%s <- %s: %s' % (
                        user['nick'].decode(),
                        channel,
                        message
                    )
                )

            }).connect()
