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

    def executeShellCommand(self, _command,  _targetDir=None):
        """
        Execute command on the shell using subprocess
        """
        # change to target dir if path was given
        if _targetDir != None:
            os.chdir(_targetDir)

        # try to execute the command 
        try:
            result = subprocess.check_output(_command, shell=True, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            result = "Error: %s" % e.output
            self.logger.debug("Error occurred: Code: %s, Text: %s" % (e.returncode, e.output))
        return result

    def handlePullCommand(self, _sender, _arguments):
        """
        Handle the 'git pull' command
        """
        if len(_arguments) == 0:
            # no arguments provided, send help
            self.sendMessage(_sender,"Usage: pull <directory>\n\nPull a directory from its origin")
            self.logger.debug("No repository name for 'pull' provided.")
        else:
            # arguments given, the first one is treated as the repository
            # all other arguments are ignored (for now)
            repository = _arguments[0]
            self.printDebugMessage(_sender, "Trying to pull repository '%s'" % repository)

            # create fully qualified path
            commandPath = os.path.join(self.gitdir,repository)

            # check if path exists at all
            # don't reveal path in return message
            if not os.path.exists(commandPath):
                self.printDebugMessage(_sender, "No git clone with name '%s' exists" % repository)
                return

            # check if constructed path is a valid git repository/clone
            if not os.path.exists(os.path.join(commandPath,".git")):
                self.printDebugMessage(_sender, "'%s' is no GIT repository" % commandPath)

            # execute git pull command and send result to sender
            result = self.executeShellCommand("git pull", commandPath)
            self.sendMessage(_sender, result)






