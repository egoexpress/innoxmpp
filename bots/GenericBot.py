# -*- coding: utf-8 -*-

"""
    GenericBot - a generic XMPP bot, works as a skeleton for special
    'worker' bots who do the actual (admin) work
    Part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

import logging              # output logging
import sleekxmpp            # XMPP communication
import configparser         # parse INI configuration file
import ssl                  # change SSL handling (for OpenFire servers)
import subprocess           # run OS commands in a shell
import os                   # perform OS operations (e.g. chdir)
import inspect              # introspection (for generic 'help' function)
import sys                  # get frame for function introspection

from framework.ConfigOptions import ConfigOptions


class GenericBot(sleekxmpp.ClientXMPP):
    """
    GenericBot - a generic bot class (skeleton for the worker bots)
    """

    def __init__(self):
        """
        Designated initializer
        """
        # set up config options
        self.configoptions = ConfigOptions()

        self.configoptions.addConfigOption(
            name="config",
            value="config/innoxmpp.ini",
            description="config file to load values from")

        self.configoptions.addConfigOption(
            name="jid",
            value="CHANGEME",
            description="XMPP ID for the bot user")

        self.configoptions.addConfigOption(
            name="password",
            value="CHANGEME",
            description="XMPP password for the bot user")

        self.configoptions.addConfigOption(
            name="openfire",
            value=1,
            description="Does the target XMPP server run OpenFire?")

        self.configoptions.addConfigOption(
            name="loglevel",
            value=logging.DEBUG,
            description="Default loglevel")

    def _cacheJIDs(self):
        """
        Cache client JIDs from roster
        These are going to be used to send push messages to

        Runs only once 5 secs after startup
        """

        # get all target JIDs from roster for JID of bot
        for targetJID in list(self.roster[self.boundjid.bare]):
            # prevent to put the bot itself in the target list
            # as we don't want to create an endless cycle of
            # sending messages FROM the bot TO the bot
            if targetJID != self.boundjid.bare:
                self.targetJIDs.append(targetJID)

    def _scheduleTasks(self):
        """
        Put tasks to be scheduled here

        To be overwritten in concrete bot implementations
        """

        # schedule caching of target JIDs
        def cacheJIDs():
            self._cacheJIDs()

        self.schedule("Cache JIDs", 5, cacheJIDs)

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
        except sleekxmpp.IQTimeout:
            self.logger.info("Timeout while getting roster")
            # TODO: handle further timeout issues
        except sleekxmpp.IQError:
            self.logger.info("Bad data received while retrieving roster")
            # TODO: handle further error issues

        # TODO: roster data is saved in self.roster/self.client_roster
        # maybe use this data as base for push messages

    def executeShellCommand(self, command,  targetDir=None):
        """
        Execute command on the shell using subprocess
        """
        # change to target dir if path was given
        if targetDir != None:
            os.chdir(targetDir)

        # try to execute the command
        try:
            result = subprocess.check_output(command,
                        shell=True,                 # run in a subshell
                        universal_newlines=True,    # always return text
                        stderr=subprocess.STDOUT    # redirect stderr to stdout
                        )
        except subprocess.CalledProcessError as e:
            result = "Error: %s" % e.output
            self.logger.debug(
                "Error occurred: Code: %s, Text: %s" % (e.returncode, e.output))
            return e.returncode, ""

        return 0, result

    def getCommandHandlerName(self, command):
        """
        Get command handler name for passed command
        """
        commandHandlerName = 'handle' + command.capitalize() + 'Command'
        self.logger.debug("COMMAND HANDLER NAME: %s" % commandHandlerName)
        return commandHandlerName

    def _getDocForCurrentFunction(self):
        """
        Return __doc__ for CALLER function
        """
        # get name as string for caller function
        # taken from http://code.activestate.com/recipes/66062/
        callerName = sys._getframe(1).f_code.co_name

        # find matching member object
        # somehow getmembers supports a predicate, but I honestly don't
        # know how it works, so I use iteration for now
        memberObjects = inspect.getmembers(self, inspect.ismethod)
        for objectName, objectRef in memberObjects:
            # check if we have found the function we want
            if objectName == callerName:
                # return stripped docstring for function reference
                return inspect.getdoc(objectRef)

    def run(self):
        """
        Startup the bot instance
        Connect to the XMPP server and start processing XMPP stanzas.
        """
        # get paramters from config file
        if os.path.exists(self.configoptions["config"]):
            config = configparser.RawConfigParser()
            config.read(self.configoptions["config"])
            self.configoptions.parseConfig(self.__class__.__name__, config)
        else:
            sys.stderr.write("Invalid config file provided!\n")
            sys.exit(2)

        # set loglevel
        logging.basicConfig(level=self.configoptions["loglevel"],
            format='%(levelname)-8s %(filename)s:%(funcName)s(%(lineno)d) %(message)s')

        # get current logger
        self.logger = logging.getLogger()

        if self.configoptions["openfire"] != "0":
            self.logger.debug("Running bot in OpenFire mode")
            self.ssl_version = ssl.PROTOCOL_SSLv3

        # setup XMPP client (super class of GenericBot)
        super(GenericBot, self).__init__(self.configoptions["jid"],
            self.configoptions["password"])

        # setup callbacks

        # handle server connection establishment
        self.add_event_handler("session_start", self.start)

        # handle received message
        self.add_event_handler("message", self.handleMessage)

        # registered JIDs for this client (i.e. the JIDs to
        # send monitoring messages to)
        self.targetJIDs = []

        # schedule tasks
        self._scheduleTasks()

        if self.connect():
            self.process(block=True)
            self.logger.info("Connection established.")
        else:
            self.logger.error("Unable to connect.")

    def printDebugMessage(self, recipient, text):
        """
        Handle debug message (send to sender and print on stdout)
        """
        self.logger.debug(text)
        self.sendMessage(recipient, text)

    def sendMessage(self, recipient, text):
        """
        Send message with given text to recipient(s)
        """
        # recipient is JID - only one recipient passed
        if isinstance(recipient, sleekxmpp.jid.JID):
            self.logger.debug("Send message '%s' to '%s'" % (text, recipient))
            self.send_message(mto=recipient, mbody=text)

        # recipient is array - multiple recipients passed
        elif isinstance(recipient, list):
            for item in recipient:
                self.logger.debug("Send message '%s' to '%s'" % (text, item))
                self.send_message(mto=item, mbody=text)

    def handleMessage(self, message):
        """
        Process incoming messages
        """
        if message['type'] in ('chat', 'normal', 'groupchat'):
            # TODO: handle groupchat messages (do I need special handling here)

            # extract message body
            messageBody = message['body']
            self.logger.debug('MESSAGE BODY: %s', messageBody)

            # get command and arguments from message
            messageParts = messageBody.split()
            command = messageParts[0]

            sender = message['from']
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
            except AttributeError:
                self.logger.info(
                    "Invalid command called, no handler found: %s" % command)
                commandHandler = None

            if not commandHandler:
                # return error if no command handler (and thus no
                # matching command) exists
                self.sendMessage(sender, "Invalid command '%s' sent!" % command)
            else:
                # execute command handler if found
                self.logger.debug("Valid command %s found, processing" % command)
                commandHandler(sender, arguments)

    # handle the (generic) 'help' command
    # collect all command handlers from the concrete bot implementation
    # by introspection and extract the docstrings
    def handleHelpCommand(self, sender, arguments):
        """
        help

        Get overview of all available commands
        """
        docStrings = []

        # get own member objects
        memberObjects = inspect.getmembers(self, inspect.ismethod)
        # traverse objects
        for objectName, objectRef in memberObjects:
            # get all command handlers
            if (objectName.startswith("handle") and \
                objectName.endswith("Command")):
                # extract docstrings and append to array
                docStrings.append(inspect.getdoc(objectRef).replace("\n\n", " - "))

        # create message, containing help header with current class (subclass of
        # GenericBot) and all help strings on separate lines
        self.sendMessage(sender, "Help for %s\n\n%s" % (
            self.__module__.split(".")[1], "\n".join(docStrings)))
