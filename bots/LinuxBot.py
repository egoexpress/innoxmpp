# -*- coding: utf-8 -*-

"""
    LinuxBot - a XMPP worker bot to perform Linux admin-related commands
    Part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

from bots.GenericBot import GenericBot

class LinuxBot(GenericBot):
    """
    LinuxBot - the Linux-related bot
    """

    def __init__(self):
        """
        Designated initializer
        """
        super(LinuxBot,self).__init__()

    def handleUptimeCommand(self, _sender, _arguments):
        """
        uptime

        Show the system uptime and load
        """
        # execute git pull command and send result to sender
        returnCode, result = self.executeShellCommand("echo $HOSTNAME && uptime")
        if returnCode == 0:
            self.sendMessage(_sender, result)