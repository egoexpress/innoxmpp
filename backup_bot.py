#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    BackupBot - an XMPP bot to control the system backup performed by duplicity
    Copyright (C) 2012 Bjoern Stierand
"""

import sys
import logging
from optparse import OptionParser
import getpass
import ConfigParser
import sleekxmpp

# force UTF8 encoding 
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

class GenericBot(sleekxmpp.ClientXMPP):

    """
    A simple bot to handle backup commands
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # handle server connection establishment
        self.add_event_handler("session_start", self.start)

        # handle received message
        self.add_event_handler("message", self.handleCommand)

        self.logger = logging.getLogger()

    def start(self, event):
        """
        Process the start of the XMPP session
        """
        self.send_presence()
        # TODO: check if we can go without roster
        #self.get_roster()

    def getCommandHandlerName(self, _command):
        commandHandlerName = 'handle' + _command.capitalize() + 'Command'
        self.logger.debug("COMMAND HANDLER NAME: %s" % commandHandlerName)
        return commandHandlerName

    def handleCommand(self, msg):
        """
        Process incoming command
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

class BackupBot(GenericBot):

    def __init__(self, jid, password):
        GenericBot.__init__(self, jid, password)
        self.loadConfigSettings()

    def loadConfigSettings(self):
        config = ConfigParser.RawConfigParser()
        config.read("innoxmpp.ini")

        self.logdir = config.get("BackupBot","logdir")
        self.logfiles = config.get("BackupBot","logfiles").split()

        self.logger.debug("Tracking backup logging dir %s" % self.logdir)
        self.logger.debug("Tracking log files %s" % self.logfiles)


    def handleStatusCommand(self, _arguments):
        """
        Handler for 'status' command
        """
        self.logger.debug("Calling the status command")
        self.logger.debug(_arguments)

            # TODO
            # write command to log file

if __name__ == '__main__':

    # get paramters from config file
    config = ConfigParser.RawConfigParser()
    config.read("innoxmpp.ini")

    jid = config.get("InnoXMPP","jid")
    password = config.get("InnoXMPP","password")
    loglevel=logging.DEBUG

    if jid is None:
        jid = raw_input("Username: ")
    if password is None:
        password = getpass.getpass("Password: ")

    # Setup logging.
    logging.basicConfig(level=loglevel,
                        format='%(levelname)-8s %(message)s')


    xmpp = BackupBot(jid, password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
