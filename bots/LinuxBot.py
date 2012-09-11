# -*- coding: utf-8 -*-

"""
    LinuxBot - a XMPP worker bot to perform Linux admin-related commands
    Part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

from bots.GenericBot import GenericBot
import os                   # needed for free space detection
import platform             # needed for free space detection

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
        self.loadConfigSettings()

    # load ini settings from config file innoxmpp.ini's [LinuxBot] section
    def loadConfigSettings(self):
        """
        Load config settings from file
        """
        # gitdir - directory where your git directories live
        self.fsdirs = self.config.get("LinuxBot","fs_directories").split()

        # githubuser - user account for github
        self.fsthreshold = self.config.getint("LinuxBot","fs_threshold")

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

    # taken from http://stackoverflow.com/questions/51658/\
    # cross-platform-space-remaining-on-volume-using-python
    # but modified (original only returns free blocks)
    def _getUsedSpaceInPercent(self, folder):
        """ 
        Return folder used space (in percent)
        """
        stats = os.statvfs(folder)
        totalSize = stats.f_blocks * stats.f_frsize
        freeSpace = stats.f_bavail * stats.f_frsize
        return 100 - (freeSpace/totalSize * 100)

    # callback to check system free space
    def taskCheckFreeSpace(self):
        """
        Check free disk space and send warning to registered users
        """
        self.logger.debug("Performing task taskCheckFreeSpace")

        resultMsg = "\n"

        # get free space (in %) for every configured mount point
        for fsdir in self.fsdirs:
            curSpace = self._getUsedSpaceInPercent(fsdir)

            # if it's above the threshold, add mount point and
            # currently used space to the result msg
            if curSpace > self.fsthreshold:
                resultMsg = resultMsg + "%-10s" % fsdir + \
                    ": %.0f%%" % curSpace + " used\n"

        # send a message to all registered JIDs if we found at least one
        # mount point who is above the threshold -> there is something
        # in the result message
        if resultMsg != "\n":

            # get current host name to include in the result message
            import socket
            curHost = socket.gethostbyaddr(socket.gethostname())[0].split(".")[0]

            # create final message and send it out
            resultMsg = "Free disk space is low on host '%s'\n" % curHost + \
                resultMsg
            for jid in self.targetJIDs:
                self.sendMessage(jid, resultMsg)