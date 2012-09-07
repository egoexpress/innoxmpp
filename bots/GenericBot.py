# -*- coding: utf-8 -*-

"""
    GenericBot - a generic XMPP bot, works as a skeleton for special 'worker' bots who
    do the actual (admin) work
    Part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

import getpass
import logging
import sleekxmpp
import configparser
import ssl
import subprocess
import os

class GenericBot(sleekxmpp.ClientXMPP):
    """
    GenericBot - a generic bot class (skeleton for the worker bots)
    """

    def __init__(self, _loglevel=logging.DEBUG):
        """
        Designated initializer
        """
        # set loglevel
        logging.basicConfig(level=_loglevel,
                            format='%(levelname)-8s %(message)s')

        # get current logger
        self.logger = logging.getLogger()

        # get paramters from config file
        self.config = configparser.RawConfigParser()
        self.config.read("config/innoxmpp.ini")

        # get jid and password for concrete bot class
        jid = self.config.get(self.__class__.__name__,"jid")
        password = self.config.get(self.__class__.__name__,"password")

        # add option to handle OpenFire servers as the manage SSL
        # a bit differently than others
        try:
            openFire = self.config.get(self.__class__.__name__,"openfire")
        except configparser.NoOptionError as e:
            openFire = "0"

        if openFire != "0":
            self.logger.debug("Running bot in OpenFire mode")
            self.ssl_version = ssl.PROTOCOL_SSLv3

        # ask for user data interactively if not found in config file
        if jid is None:
            jid = raw_input("Username: ")
        if password is None:
            password = getpass.getpass("Password: ")

        # setup XMPP client (super class of GenericBot)
        super(GenericBot, self).__init__(jid, password)

        # setup callbacks

        # handle server connection establishment
        self.add_event_handler("session_start", self.start)

        # handle received message
        self.add_event_handler("message", self.handleMessage)

        # TODO: check if we need any of these
        #self.register_plugin('xep_0030') # Service Discovery
        #self.register_plugin('xep_0004') # Data Forms
        #self.register_plugin('xep_0060') # PubSub
        #self.register_plugin('xep_0199') # XMPP Ping

    def start(self, event):
        """
        Process the start of the XMPP session
        """
        # send presence to server (required by spec)
        self.send_presence()

        # although we don't necessarily need to get the roster
        # the spec forces us to get it, otherwise some servers may not deliver
        # or send messages to us (ejabberd doesn't care)
        try: 
            self.get_roster()
        except IQTimeout as e:
            self.logger.info("Timeout while getting roster")
            # TODO: handle further timeout issues
        except IQError as e:
            self.logger.info("Bad data received while retrieving roster")
            # TODO: handle further error issues

        # TODO: roster data is saved in self.roster/self.client_roster
        # maybe use this data as base for push messages

    def executeShellCommand(self, _command,  _targetDir=None):
        """
        Execute command on the shell using subprocess
        """
        # change to target dir if path was given
        if _targetDir != None:
            os.chdir(_targetDir)

        # try to execute the command 
        try:
            result = subprocess.check_output(_command, 
                        shell=True,                 # run in a subshell
                        universal_newlines=True,    # always return text
                        stderr=subprocess.STDOUT    # redirect stderr to stdout
                        )
        except subprocess.CalledProcessError as e:
            result = "Error: %s" % e.output
            self.logger.debug("Error occurred: Code: %s, Text: %s" % (e.returncode, e.output))
            return e.returncode, ""

        return 0, result

    def getCommandHandlerName(self, _command):
        """
        Get command handler name for passed command
        """
        commandHandlerName = 'handle' + _command.capitalize() + 'Command'
        self.logger.debug("COMMAND HANDLER NAME: %s" % commandHandlerName)
        return commandHandlerName

    def run(self):
        """
        Connect to the XMPP server and start processing XMPP stanzas.
        """
        if self.connect():
            self.process(block=True)
            print("Done")
        else:
            print("Unable to connect.")

    def printDebugMessage(self, _recipient, _text):
        """
        Handle debug message (send to sender and print on stdout)
        """
        self.logger.debug(_text)
        self.sendMessage(_recipient,_text)

    def sendMessage(self, _recipient, _text):
        """
        Send message with given _text to _recipient
        """
        self.logger.debug("Send message '%s' to '%s'" % (_text, _recipient))
        self.send_message(mto=_recipient,mbody=_text)

    def handleMessage(self, _msg):
        """
        Process incoming messages
        """
        if _msg['type'] in ('chat', 'normal','groupchat'):
            # TODO: handle groupchat messages (do I need special handling here)

            # extract message body
            messageBody = _msg['body']
            self.logger.debug('MESSAGE BODY: %s', messageBody)

            # get command and arguments from message
            messageParts = messageBody.split()
            command = messageParts[0]

            sender = _msg['from']
            self.logger.debug('MESSAGE FROM: %s' % sender)

            arguments = []
            if len(messageParts) > 0:
                arguments = messageParts[1:]
            self.logger.debug('COMMAND: %s', command)
            self.logger.debug('ARGUMENTS: %s', arguments)

            # check if the command is valid at akk
            commandHandlerName = self.getCommandHandlerName(command)
            # try to get command handler using reflection
            try:
                commandHandler = getattr(self, commandHandlerName)
            except AttributeError as a:
                self.logger.info("Invalid command called, no handler found: %s" % command)
                commandHandler = None

            if not commandHandler:
                # return error if no command handler (and thus no matching command) exists
                self.sendMessage(sender, "Invalid command '%s' sent!" % command)
            else:
                # execute command handler if found
                self.logger.debug("Valid command %s found, processing" % command)
                commandHandler(sender, arguments)
