#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Generic - a generic XMPP bot, works as a skeleton for special 'worker' bots who
    do the actual work
    Copyright (C) 2012 Bjoern Stierand
"""

import getpass
import logging
import sleekxmpp
import ConfigParser

class GenericBot(sleekxmpp.ClientXMPP):

    """
    A generic bot class (skeleton for the worker bots)
    """

    def __init__(self):

        # get paramters from config file
        config = ConfigParser.RawConfigParser()
        config.read("config/innoxmpp.ini")

        jid = config.get("InnoXMPP","jid")
        password = config.get("InnoXMPP","password")

        # ask for user data interactively
        if jid is None:
            jid = raw_input("Username: ")
        if password is None:
            password = getpass.getpass("Password: ")

        # setup XMPP client
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # handle server connection establishment
        self.add_event_handler("session_start", self.start)

        # handle received message
        self.add_event_handler("message", self.handleMessage)

        self.logger = logging.getLogger()

    def start(self, event):
        """
        Process the start of the XMPP session
        """
        self.send_presence()

    def getCommandHandlerName(self, _command):
        """
        Get command handler name for passed command
        """

        commandHandlerName = 'handle' + _command.capitalize() + 'Command'
        self.logger.debug("COMMAND HANDLER NAME: %s" % commandHandlerName)
        return commandHandlerName

    def handleMessage(self, msg):
        """
        Process incoming message
        """
        if msg['type'] in ('chat', 'normal'):
            messageBody = msg['body']
            self.logger.debug('MESSAGE BODY: %s', messageBody)

            command = messageBody.split()[0]
            arguments = messageBody.split()[1:]
            self.logger.debug('COMMAND: %s', command)

            # check if the command is valid at all
            commandHandlerName = self.getCommandHandlerName(command)
            try:
                commandHandler = getattr(self, commandHandlerName)
            except AttributeError, a:
                self.logger.info("Invalid command called, no handler found: %s" % command)
                commandHandler = None

            if not commandHandler:
                msg.reply("Invalid command %s sent!" % command).send()
            else:
                self.logger.debug("Valid command %s found, processing" % command)
                commandHandler(arguments)