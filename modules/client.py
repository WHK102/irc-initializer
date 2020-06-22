#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import threading
import re


class Client:

    def __init__(self):

        # Variables
        self.threadReceive = None
        self.socket        = None
        self.user          = {
            'nick': None
        }

        # Eventos
        self.onConnecting            = None
        self.onConnect               = None
        self.onDisconnect            = None
        self.onSendCommand           = None
        self.onReceive               = None
        self.onReceivePrivateMessage = None
        self.onReceiveChannelMessage = None


    def connect(self, host, port):

        # Antes de reconectar, debe desconectar
        if(self.socket):
            self.disconnect()

        # Llama al evento si está definido
        if(self.onConnecting is not None):
            self.onConnecting(host, port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(None)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((str(host), int(port)))

        # Llama al evento si está definido
        if(self.onConnect is not None):
            self.onConnect(host, port)

        self.threadReceive = threading.Thread(target = self.receiver)
        self.threadReceive.start()


    def disconnect(self):

        # Llama al evento si está definido
        if(self.onDisconnect is not None):
            self.onDisconnect()

        if(self.socket):
            self.socket.shutdown(1)
            self.socket.close()

        self.socket = None


    def login(self, nick, password):

        if(not isinstance(nick, bytes)):
            nick = str(nick).encode()

        if(not isinstance(password, bytes)):
            nick = str(password).encode()

        self.user['nick'] = nick

        self.sendCommand(b'NICK', self.user['nick'])
        self.sendCommand(b'USER', self.user['nick'] + '  8 x : ' + self.user['nick'])

        # TODO: user password


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


    def sendPrivateMessage(toNick, message):

        if(not isinstance(toNick, bytes)):
            toNick = str(toNick).encode()

        if(not isinstance(message, bytes)):
            message = str(message).encode()

        self.sendCommand(b'PRIVMSG', toNick + b' :' + message)


    def receiver(self):

        # Memoria asignada para el rellenado temporal del buffer hasta ir
        # extrayendo cada línea detectada.
        lastBuffer = b''

        while(True):

            # Acumula el buffer de entrada hasta encontrar un salto de línea,
            # esto delimita cada respuesta del servidor
            data = self.socket.recv(1024)
            if data:
                lastBuffer += data
                if b'\n' in lastBuffer:
                    lines = lastBuffer.split(b'\n')
                    lastBuffer = lines.pop()

                    # Procesa cada linea de respuesta del servidor IRC
                    for line in lines:

                        # Limpia la línea de los saltos de líneas finales agregados
                        line = line.strip()

                        # Estructura de la respuesta del servidor
                        response = {
                            'from'    : None, # Servidor
                            'type'    : None, # Tipo de mensaje
                            'to'      : None, # Usuario
                            'value'   : None, # Valor del mensaje
                            'message' : None  # Mensaje
                        }

                        # Desglosa la línea
                        matches = re.search(
                            # Detecta respuestas de mensajes con valores
                            br'^:(.+?)\s+(.+?)\s+(.+?)\s+(.+?):(.+)$',
                            line
                        )
                        if(matches):
                            response['from']    = matches.group(1)
                            response['type']    = matches.group(2)
                            response['to']      = matches.group(3)
                            response['value']   = matches.group(4)
                            response['message'] = matches.group(5)

                        else:
                            matches = re.search(
                                # Detecta respuestas de mensajes sin valores
                                br'^:(.+?)\s+(.+?)\s+(.+?)\s*:(.+)$',
                                line
                            )
                            if(matches):
                                response['from']    = matches.group(1)
                                response['type']    = matches.group(2)
                                response['to']      = matches.group(3)
                                response['value']   = None
                                response['message'] = matches.group(4)

                            else:
                                matches = re.search(
                                    # Detecta respuesta de valores sin mensajes
                                    br'^:(.+?)\s+(.+?)\s+(.+?)\s+(.+)$',
                                    line
                                )
                                if(matches):
                                    response['from']    = matches.group(1)
                                    response['type']    = matches.group(2)
                                    response['to']      = matches.group(3)
                                    response['value']   = matches.group(4)
                                    response['message'] = None

                                else:
                                    matches = re.search(
                                        # Respuestas de bajo nivel
                                        br'^(\w+)\s*:(.+)$',
                                        line
                                    )
                                    if(matches):
                                        response['from']    = None
                                        response['type']    = matches.group(1)
                                        response['to']      = None
                                        response['value']   = None
                                        response['message'] = matches.group(2)

                                    else:
                                        # El servidor ha enviado una línea fuera
                                        # del estandar o no controlada.
                                        
                                        if(self.onReceive is not None):
                                            self.onReceive(
                                                rawLine  = line,
                                                response = None
                                            )
                                       
                                        continue

                        # Llama al evento si está definido
                        if(self.onReceive is not None):
                            self.onReceive(
                                rawLine  = line,
                                response = response
                            )

                        if(response['type'] == b'NOTICE'):
                            # Noticia o comentario de servidor
                            pass

                        elif(response['type'] == b'001'):
                            # Mensaje de bienvenida
                            pass

                        elif(response['type'] == b'002'):
                            # Host y version del servidor
                            pass

                        elif(response['type'] == b'003'):
                            # Fecha de creación del servidor
                            pass

                        elif(response['type'] == b'005'):
                            # Prefijos y protocolos soportados
                            pass

                        elif(response['type'] == b'042'):
                            # Id único de la conexión
                            pass

                        elif(response['type'] == b'375'):
                            # Inicio del mensaje del día
                            pass

                        elif(response['type'] == b'372'):
                            # Parte del mensaje del día
                            pass

                        elif(response['type'] == b'376'):
                            # Final del mensaje del día
                            pass

                        elif(response['type'] == b'251'):
                            # Estadísticas del servidor (usuarios conectados y servidores disponibles)
                            pass

                        elif(response['type'] == b'252'):
                            # Cantidad de operadores en línea
                            pass

                        elif(response['type'] == b'254'):
                            # Cantidad de canales creados
                            pass

                        elif(response['type'] == b'255'):
                            # Estadísticas de conexión (clientes v/s servidores)
                            pass

                        elif(response['type'] == b'265'):
                            # Cantidad de usuarios locales máximos
                            pass

                        elif(response['type'] == b'266'):
                            # Cantidad de usuarios globales máximos
                            pass

                        elif(response['type'] == b'396'):
                            # Nombre de host asignado a la conexión
                            pass

                        elif(response['type'] == b'396'):
                            # Nombre de host asignado a la conexión
                            pass

                        elif(response['type'] == b'MODE'):
                            # Modo (permisos)
                            pass

                        elif(response['type'] == b'MODE'):
                            # Modo (permisos)
                            pass

                        elif(response['type'] == b'PING'):
                            # Ping
                            
                            self.sendCommand('PONG', response['message'])

                        elif(response['type'] == b'PRIVMSG'):
                            # Mensaje entrante

                            if(
                                (response['value'] and self.user['nick']) and
                                (response['value'] == self.user['nick'])
                            ):
                                # Mensaje privado entrante
                                if(self.onReceivePrivateMessage is not None):
                                    self.onReceivePrivateMessage(
                                        user=self.decomposeUser(response['from']),
                                        message=response['message']
                                    )
                            else:
                                # Mensaje del canal
                                if(self.onReceiveChannelMessage is not None):
                                    self.onReceiveChannelMessage(
                                        channel=response['value'],
                                        user=self.decomposeUser(response['from']),
                                        message=response['message']
                                    )

            else:
                break

        # Hubo una desconexión desde el servidor
        self.disconnect()


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


    def sendCommand(self, command, arguments):

        if(not isinstance(command, bytes)):
            command = str(command).encode()

        if(not isinstance(arguments, bytes)):
            arguments = str(arguments).encode()

        # Llama al evento si está definido
        if(self.onSendCommand is not None):
            self.onSendCommand(command, arguments)

        # Envía el comando al servidor IRC
        self.socket.send(
            command.upper() + b' ' + arguments + b'\r\n'
        )
