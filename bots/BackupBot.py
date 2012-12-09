# -*- coding: utf-8 -*-

"""
    BackupBot - a XMPP worker bot to perform backup-related commands
    Part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

from bots.GenericBot import GenericBot


class BackupBot(GenericBot):

    def __init__(self):
        """
        Designated initializer
        """
        super(BackupBot, self).__init__()

        self.configoptions.addConfigOption(
            name="logdir",
            value="/tmp",
            description="directory to track")

        self.configoptions.addConfigOption(
            name="logfiles",
            value="CHANGEME",
            description="logfiles to track")

    def run(self):
        super(BackupBot, self).run()
        self.logger.debug("Tracking backup logging dir %s" % self.logdir)
        self.logger.debug("Tracking log files %s" % self.logfiles)

    def handleStatusCommand(self, message, arguments):
        """
        Handler for 'status' command
        """
        self.logger.debug("Calling the status command")
        self.logger.debug(arguments)

        # TODO
        # write command to log file
