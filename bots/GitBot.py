# -*- coding: utf-8 -*-

"""
    GitBot - a XMPP worker bot to perform git-related commands
    part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

from bots.GenericBot import GenericBot
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

    def sanitizeArguments(self, _sender, _textArgument):
        """
        Sanitize input, reject if it contains suspicious characters
        """

        errorMsg = ""

        # return error code if it contains ";" or "&"
        self.logger.debug("=========")
        self.logger.debug(_textArgument.find("&"))
        if _textArgument.find("&") != -1 or _textArgument.find(";") != -1:
            errorMsg = "ERROR: Invalid character found in argument"

        if errorMsg != "":
            self.sendMessage(_sender, errorMsg)
            return 1, errorMsg

        return 0, _textArgument

    def _getGitRepositoryPath(self, _sender, _repository):
        # create fully qualified path
        commandPath = os.path.join(self.gitdir, _repository)

        # check if path exists at all
        # don't reveal path in return message
        if not os.path.exists(commandPath):
            self.printDebugMessage(_sender, "No git clone with name '%s' exists" % _repository)
            return 1, ""

        # check if constructed path is a valid git repository/clone
        if not os.path.exists(os.path.join(commandPath,".git")):
            self.printDebugMessage(_sender, "'%s' is no GIT repository" % commandPath)
            return 1, ""

        return 0, commandPath

    def handleCommitCommand(self, _sender, _arguments):
        """
        commit <repository> [<message>]

        Commit current state of <repository> using optional <message>
        """
        if len(_arguments) == 0:
            # no arguments provided, send help
            # TODO: use docstring of function
            self.sendMessage(_sender,
                "Usage: commit <directory> <message>\n\nCommit directory using given message.")
            self.logger.debug("No repository name for 'commit' provided.")
        else:
            repository = _arguments[0]
            self.printDebugMessage(_sender, 
                "Trying to commit repository '%s'" % repository)

            returnCode = 0

            if len(_arguments) > 1:
                commitMsg = ' '.join(_arguments[1:])
                returnCode, commitMsg = self.sanitizeArguments(
                    _sender, commitMsg)
            else:
                commitMsg = "Autocommit using GitBot"

            if returnCode == 0:
                returnCode, commandPath = \
                    self._getGitRepositoryPath(_sender, repository)
                if returnCode == 0:
                    # execute git commit command and send result to sender
                    returnCode, result = \
                        self.executeShellCommand(
                            "git commit -a -m \"%s\"" % commitMsg, commandPath)
                    if returnCode == 0:
                        self.sendMessage(_sender, result)
                    elif returnCode == 1:
                        self.sendMessage(_sender, "Nothing to commit")

    def handlePullCommand(self, _sender, _arguments):
        """
        pull <repository>

        Pull a directory from its origin
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

            returnCode, commandPath = self._getGitRepositoryPath(_sender, repository)
            if returnCode == 0:
                # execute git pull command and send result to sender
                returnCode, result = self.executeShellCommand("git pull", commandPath)
                if returnCode == 0:
                    self.sendMessage(_sender, result)

    # handle the 'git push' command
    def handlePushCommand(self, _sender, _arguments):
        """
        push <repository>

        Push a given directory to its origin"
        """
        if len(_arguments) == 0:
            # no arguments provided, send help
            self.sendMessage(_sender,"Usage: push <directory>\n\nPush a directory to its origin")
            self.logger.debug("No repository name for 'push' provided.")
        else:
            # arguments given, the first one is treated as the repository
            # all other arguments are ignored (for now)
            repository = _arguments[0]
            self.printDebugMessage(_sender, "Trying to push repository '%s'" % repository)

            returnCode, commandPath = self._getGitRepositoryPath(_sender, repository)
            if returnCode == 0:
                # execute git push command and send result to sender
                returnCode, result = self.executeShellCommand("git push", commandPath)
                if returnCode == 0:
                    self.sendMessage(_sender, result)