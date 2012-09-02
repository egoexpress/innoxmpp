from GenericBot import GenericBot

import ConfigParser
import logging

class GitBot(GenericBot):

    def __init__(self, jid, password):
        GenericBot.__init__(self, jid, password)
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


    xmpp = GitBot(jid, password)
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
