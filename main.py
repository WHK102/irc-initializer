#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse
import time
from app.controllers.main import MainController
from app.controllers.help import HelpController
from app.service.config import ConfigService


class Route:

    def __init__(self):

        # Services
        configService = ConfigService()

        # Vars
        config = None

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

        # Help argument
        if(argparseParsed.help):

            # Construct & call the controller
            HelpController()
            return

        # Load config if exist
        config = configService.getFromFile(
            argparseParsed.config if argparseParsed.config else (
                os.path.dirname(os.path.abspath(__file__)) + '/config.json'
            )
        )

        # Construct & call the controller
        MainController(config)


if __name__ == '__main__':

    # Construct & call the route
    Route()
