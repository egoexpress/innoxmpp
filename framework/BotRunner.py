# -*- coding: utf-8 -*-

"""
    BotRunner - a running class for innoxmpp bots
    Part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

import argparse
import logging


class BotRunner():
    """
    BotRunner - execute bots and handle command line input
    """

    def __init__(self, botclass):
        """
        Designated initializer

        botclass - bot class that should be executed
        """
        # cache bot class and set the instance up
        self.botInstance = botclass()

        # set up logging for the bot runner
        logging.basicConfig(level=logging.DEBUG,
            format='%(levelname)-8s %(filename)s:%(funcName)s(%(lineno)d) %(message)s')
        self.logger = logging.getLogger()

        # set up argument parser
        self.parser = argparse.ArgumentParser()

        # get configuration from bot class
        # add config values to arg parser
        # TODO: clean this up
        for key, value in self.botInstance.configoptions.options.items():
            self.logger.debug("Adding value %s" % key)
            self.parser.add_argument("--%s" % key,
                help=value["description"])

    def run(self):
        """
        run the bot instance
        """
        # parse comnmand line arguments
        arguments = self.parser.parse_args()

        self.botInstance.configoptions.processCommandLineArguments(vars(arguments))

        # run bot class,
        self.botInstance.run()
