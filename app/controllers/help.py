#!/usr/bin/python
# -*- coding: utf-8 -*-


class HelpController(object):


    def __init__(self):

        pass


    def print(self):

        print('\n'.join([
            '-h, --help            Muestra el mensaje de ayuda.',
            '-c, --config [path]   Carga el archivo de configuración específico,',
            '                      en caso contrario utilizará el archivo config.json',
            '                      localizado en la raiz del script.'
        ]))