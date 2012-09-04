# -*- coding: utf-8 -*-

"""
    GitBot - a XMPP worker bot to perform git-related commands
    part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

from bots.GenericBot import GenericBot
import subprocess
import os

class GitBot(GenericBot):
    """
    GitBot - the git-related bot
    """

    def __init__(self):
        """
        Designated initializer
        """
        super(GitBot,self).__init__()
        self.loadConfigSettings()

    def loadConfigSettings(self):
        """
        Load config settings from file
        """
        self.gitdir = self.config.get("GitBot","gitdir")
        self.githubuser = self.config.get("GitBot","githubuser")

    def handlePullCommand(self, _sender, _arguments):
        """
        Handle the 'git pull' command
        """
        if len(_arguments) == 0:
            # no arguments provided, send help
            self.sendMessage(_sender,"Usage: pull <directory>\n\nPull a directory from its origin")
            self.logger.debug("No repository name for 'pull' provided.")
        else:
            repository = _arguments[0]
            self.printDebugMessage(_sender, "Trying to pull repository '%s'" % repository)

            commandPath = os.path.join(self.gitdir,repository)

            if not os.path.exists(commandPath):
                self.printDebugMessage(_sender, "Invalid directory name '%s'" % commandPath)
                return

            if not os.path.exists(os.path.join(commandPath,".git")):
                self.printDebugMessage(_sender, "'%s' is no GIT repository" % commandPath)

            # TODO: works for now, but now I need to grep stdout/stderr and send it back to
            # the sender
            os.chdir(commandPath)
            result = subprocess.check_output("git pull", shell=True, universal_newlines=True)
            self.sendMessage(_sender, result)






