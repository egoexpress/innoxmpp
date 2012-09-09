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

    # initialize class
    def __init__(self):
        """
        Designated initializer
        """
        super(LinuxBot,self).__init__()

    def _scheduleTasks(self):
        """
        add tasks to be scheduled to global scheduler

        The scheduler needs a callback to be called after the given interval
        has passed. As it accepts no class functions as callback, we create a
        wrapper using a local function which calls the class function
        """

        super(LinuxBot,self)._scheduleTasks()

        # schedule checking of free space
        def checkFreeSpace():
            self.taskCheckFreeSpace()

        self.schedule("Check Free Space", 60, checkFreeSpace, repeat=True)

    # handler for the Linux 'uptime' command
    def handleUptimeCommand(self, _sender, _arguments):
        """
        uptime

        Show the system uptime and load
        """
        # execute git pull command and send result to sender
        returnCode, result = self.executeShellCommand("echo $HOSTNAME && uptime")
        if returnCode == 0:
            self.sendMessage(_sender, result)

    # callback to check system free space
    def taskCheckFreeSpace(self):
        """
        Check free disk space and send warning to registered users
        """
        self.logger.debug("Performing task taskCheckFreeSpace")

        # TODO: implement logic here

        # for jid in self.targetJIDs:
            # self.sendMessage(jid, "Test Message")