#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import threading
import re


class IrcClient(object):


    def __init__(self, host, port):

        self.host = host
        self.port = port

        # Vars
        self.threadReceive = None
        self.socket        = None
        self.user          = {
            'nick': None
        }

        # Multi-events
        self.onConnecting            = [ ]
        self.onConnect               = [ ]
        self.onDisconnect            = [ ]
        self.onSendCommand           = [ ]
        self.onRawReceive            = [ ]
        self.onReceive               = [ ]
        self.onReceivePrivateMessage = [ ]
        self.onReceiveChannelMessage = [ ]
        self.onJoinChannel           = [ ]


    def setOnConnecting(self, onConnecting):

        self.onConnecting.insert(0, onConnecting)
        return self

    
    def setOnConnect(self, onConnect):

        self.onConnect.insert(0, onConnect)
        return self

    
    def setOnDisconnect(self, onDisconnect):

        self.onDisconnect.insert(0, onDisconnect)
        return self

    
    def setOnSendCommand(self, onSendCommand):

        self.onSendCommand.insert(0, onSendCommand)
        return self

    
    def setOnRawReceive(self, onRawReceive):

        self.onRawReceive.insert(0, onRawReceive)
        return self


    def setOnReceive(self, onReceive):

        self.onReceive.insert(0, onReceive)
        return self

    
    def setOnReceivePrivateMessage(self, onReceivePrivateMessage):

        self.onReceivePrivateMessage.insert(0, onReceivePrivateMessage)
        return self

    
    def setOnReceiveChannelMessage(self, onReceiveChannelMessage):

        self.onReceiveChannelMessage.insert(0, onReceiveChannelMessage)
        return self

    
    def setOnJoinChannel(self, onJoinChannel):

        self.onJoinChannel.insert(0, onJoinChannel)
        return self


    def connect(self):
        
        # Call events
        if(len(self.onConnecting)):
            for event in self.onConnecting:
                event()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(None)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((str(self.host), int(self.port)))

        if(len(self.onConnect)):
            for event in self.onConnect:
                event()

        self.threadReceive = threading.Thread(target = self.receiver)
        self.threadReceive.start()


    def receiver(self):

        # Stack of the bytes from the socker client
        lastBuffer = b''

        while(True):

            data = self.socket.recv(1024)
            if(data):

                lastBuffer += data
                if(b'\n' in lastBuffer):

                    lines = lastBuffer.split(b'\n')
                    lastBuffer = lines.pop()

                    for line in lines:
                        self.parseResponseLine(line)

            else:
                break

        # Disconnected from IRC Server
        self.disconnect()


    def parseResponseLine(self, line):

        # Filters
        line = line.strip()

        if(len(self.onRawReceive)):
            for event in self.onRawReceive:
                event(rawLine=line)

        # Parse line

        # Detect message responses with values
        matches = re.search(
            br'^:(.+?)\s+(.+?)\s+(.+?)\s+(.+?):(.+)$',
            line
        )
        if(matches):
            self.parseResponseData({
                'from'    : matches.group(1),
                'type'    : matches.group(2),
                'to'      : matches.group(3),
                'value'   : matches.group(4),
                'message' : matches.group(5)
            })
            return

        # Detect message responses without values
        matches = re.search(
            br'^:(.+?)\s+(.+?)\s+(.+?)\s*:(.+)$',
            line
        )
        if(matches):
            self.parseResponseData({
                'from'    : matches.group(1),
                'type'    : matches.group(2),
                'to'      : matches.group(3),
                'value'   : None,
                'message' : matches.group(4)
            })
            return

        # Detect response of values without messages
        matches = re.search(
            br'^:(.+?)\s+(.+?)\s+(.+?)\s+(.+)$',
            line
        )
        if(matches):
            self.parseResponseData({
                'from'    : matches.group(1),
                'type'    : matches.group(2),
                'to'      : matches.group(3),
                'value'   : matches.group(4),
                'message' : None
            })
            return

        # Low level response
        matches = re.search(
            br'^(\w+)\s*:(.+)$',
            line
        )
        if(matches):
            self.parseResponseData({
                'from'    : None,
                'type'    : matches.group(1),
                'to'      : None,
                'value'   : None,
                'message' : matches.group(2)
            })
            return

        # Unknown response structure


    def parseResponseData(self, response):

        if(len(self.onReceive)):
            for event in self.onReceive:
                event(response=response)

        if(response['type'] == b'NOTICE'):
            # Notice or comments
            pass

        elif(response['type'] == b'001'):
            # Welcome message
            pass

        elif(response['type'] == b'002'):
            # Hostname and IRC Server version
            pass

        elif(response['type'] == b'003'):
            # Date of creation of IRC Server
            pass

        elif(response['type'] == b'005'):
            # Prefixes and protocols supported
            pass

        elif(response['type'] == b'042'):
            # Connection unique id
            pass

        elif(response['type'] == b'375'):
            # Bigen of message of the day
            pass

        elif(response['type'] == b'372'):
            # Message of the day chunk
            pass

        elif(response['type'] == b'376'):
            # End of message of the day
            pass

        elif(response['type'] == b'251'):
            # Server statics
            pass

        elif(response['type'] == b'252'):
            # Ops count
            pass

        elif(response['type'] == b'254'):
            # Channels count
            pass

        elif(response['type'] == b'255'):
            # Client/Server connections statics
            pass

        elif(response['type'] == b'265'):
            # Max local users
            pass

        elif(response['type'] == b'266'):
            # Max users globals
            pass
            
        elif(response['type'] == b'366'):
            # End of users list
            pass
#            if(len(self.onJoinChannel)):
#                for event in self.onJoinChannel:
#                    event()

        elif(response['type'] == b'396'):
            # Set hostname from IRC Server
            pass

        elif(response['type'] == b'MODE'):
            # Mode
            pass

        elif(response['type'] == b'PING'):
            # Ping
            
            self.sendCommand('PONG', response['message'])

        elif(response['type'] == b'PRIVMSG'):

            print([response, self.user])
            if(
                (response['to'] and (response['to'][0] == b'#'))
            ):
                # To channel message
                if(len(self.onReceiveChannelMessage)):
                    for event in self.onReceiveChannelMessage:
                        event(
                            channel=response['value'],
                            user=self.decomposeUser(response['from']),
                            message=response['message']
                        )
            else:
                # Private message
                if(len(self.onReceivePrivateMessage)):
                    for event in self.onReceivePrivateMessage:
                        event(
                            user=self.decomposeUser(response['from']),
                            message=response['message']
                        )


    def disconnect(self):

        if(len(self.onDisconnect)):
            for event in self.onDisconnect:
                event()

        if(self.socket):
            self.socket.shutdown(1)
            self.socket.close()

        self.socket = None


    def setNick(self, nick):

        if(not isinstance(nick, bytes)):
            nick = str(nick).encode()

        self.user['nick'] = nick

        self.sendCommand(b'NICK', self.user['nick'])
        self.sendCommand(b'USER', self.user['nick'] + b'  8 x : ' + self.user['nick'])


    def joinChannel(self, channel):

        if(not isinstance(channel, bytes)):
            channel = str(channel).encode()

        self.sendCommand(b'JOIN', channel)


    def sendPrivateMessage(self, toNick, message):

        if(not isinstance(toNick, bytes)):
            toNick = str(toNick).encode()

        if(not isinstance(message, bytes)):
            message = str(message).encode()

        self.sendCommand(b'PRIVMSG', toNick + b' :' + message)


    def sendMessageToChannel(self, channel, message):

        if(not isinstance(channel, bytes)):
            channel = str(channel).encode()

        if(not isinstance(message, bytes)):
            message = str(message).encode()

        self.sendCommand(b'PRIVMSG', channel + b' :' + message)


    def decomposeUser(self, fullId):
        
        user = {
            'nick'     : None,
            'name'     : None,
            'hostname' : None
        }

        matches = re.search(br'^(.+?)!(.+?)@(.+)$', fullId)
        if(matches):
            user['nick']     = matches.group(1)
            user['name']     = matches.group(2)
            user['hostname'] = matches.group(3)
        
        return user


    def send(self, composed):

        if(not isinstance(composed, bytes)):
            composed = str(composed).encode()

        matches = re.search(br'^/.+? .+', composed)
        if(matches):
            self.sendCommand(matches.group(1).upper(), matches.group(2))


    def sendCommand(self, command, arguments):

        if(not isinstance(command, bytes)):
            command = str(command).encode()

        if(not isinstance(arguments, bytes)):
            arguments = str(arguments).encode()

        if(len(self.onSendCommand)):
            for event in self.onSendCommand:
                event(command=command, arguments=arguments)

        # Send the command to IRC Server
        self.socket.send(
            command.upper() + b' ' + arguments + b'\r\n'
        )


class IrcService(object):

    def __init__(self):

        pass


    def createClient(self, host, port):

        return IrcClient(host, port)
