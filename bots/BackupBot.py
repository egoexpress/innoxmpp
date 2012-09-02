from GenericBot import GenericBot

import ConfigParser

class BackupBot(GenericBot):

    def __init__(self):
        GenericBot.__init__(self)
        self.loadConfigSettings()

    def loadConfigSettings(self):
        config = ConfigParser.RawConfigParser()
        config.read("config/innoxmpp.ini")

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