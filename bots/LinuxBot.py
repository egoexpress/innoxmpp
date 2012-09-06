# -*- coding: utf-8 -*-

"""
    LinuxBot - a XMPP worker bot to perform Linux admin-related commands
    Part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

from bots.GenericBot import GenericBot
import subprocess

class LinuxBot(GenericBot):
    """
    LinuxBot - the Linux-related bot
    """

    def __init__(self):
        """
        Designated initializer
        """
        super(LinuxBot,self).__init__()

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
        return result

    def handleUptimeCommand(self, _sender, _arguments):
        """
        Handle the 'uptime' command
        """
        # execute git pull command and send result to sender
        result = self.executeShellCommand("echo $HOSTNAME && uptime")
        self.sendMessage(_sender, result)






