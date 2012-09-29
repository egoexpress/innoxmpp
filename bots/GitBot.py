# -*- coding: utf-8 -*-

"""
    GitBot - a XMPP worker bot to perform git-related commands
    Part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

from bots.GenericBot import GenericBot
import os

class GitBot(GenericBot):
    """
    GitBot - the git-related bot
    """

    # initialize class
    def __init__(self):
        """
        Designated initializer
        """
        super(GitBot,self).__init__()
        self.loadConfigSettings()

    # load ini settings from config file innoxmpp.ini's [GitBot] section
    def loadConfigSettings(self):
        """
        Load config settings from file
        """
        # gitdir - directory where your git directories live
        self.gitdir = self.config.get("GitBot","gitdir")

        # githubuser - user account for github
        self.githubuser = self.config.get("GitBot","githubuser")

    # clean up arguments sent by the client to avoid execution of
    # arbitrary shell commands (e.g. by supplying arguments including
    # characters as ';' or '&')
    def _sanitizeArguments(self, _sender, _textArgument):
        """
        Sanitize input, reject if it contains suspicious characters
        that could lead to execution of arbitrary shell commands
        """
        errorMsg = ""

        # return error code if it contains ";" or "&"
        if _textArgument.find("&") != -1 or _textArgument.find(";") != -1:
            errorMsg = "ERROR: Invalid character found in argument"

        # if an error occurred (that is, an error msg is set, return 1
        if errorMsg != "":
            self.sendMessage(_sender, errorMsg)
            return 1, errorMsg

        # no error occurred, return 0 and the input argument
        return 0, _textArgument

    # construct fully qualified repository path for given _repository
    # plus some sanity checks (e.g. if the dir is a valid repository)
    def _getGitRepositoryPath(self, _sender, _repository):
        """
        ___getGitRepositoryPath(_sender, _repository)

        create fully qualified name for _repository using the
        ini setting 'gitdir', send error messages to _sender
        """

        # create fully qualified path
        commandPath = os.path.join(self.gitdir, _repository)

        # check if path exists at all
        # don't reveal path in return message
        if not os.path.exists(commandPath):
            self.printDebugMessage(_sender, 
                "No git clone with name '%s' exists" % _repository)
            return 1, ""

        # check if constructed path is a valid git repository/clone
        if not os.path.exists(os.path.join(commandPath,".git")):
            self.printDebugMessage(_sender, 
                "'%s' is no GIT repository" % commandPath)
            return 1, ""

        return 0, commandPath

    # handler for the 'git commit -a [-m <message>]' command
    def handleCommitCommand(self, _sender, _arguments):
        """
        commit <repository> [<message>]

        Commit current state of <repository> using optional <message>
        """
        if len(_arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(_sender,
                "Usage: %s" % self._getDocForCurrentFunction())
            self.logger.debug("No repository name for 'commit' provided.")
        else:
            repository = _arguments[0]
            self.printDebugMessage(_sender, 
                "Trying to commit repository '%s'" % repository)

            returnCode = 0

            if len(_arguments) > 1:
                commitMsg = ' '.join(_arguments[1:])
                returnCode, commitMsg = self._sanitizeArguments(
                    _sender, commitMsg)
            else:
                commitMsg = "Autocommit using GitBot"

            # we can safely ignore the case when the returnCode was != 0
            # as an error message is sent my _sanitizeArguments
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

    # handler for the 'git pull' command
    def handlePullCommand(self, _sender, _arguments):
        """
        pull <repository>

        Pull a directory from its origin
        """
        if len(_arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(_sender,
                "Usage: %s", self._getDocForCurrentFunction())
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

    # handler for the 'git push' command
    def handlePushCommand(self, _sender, _arguments):
        """
        push <repository>

        Push a given directory to its origin"
        """
        if len(_arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(_sender,
                "Usage: %s" % self._getDocForCurrentFunction())
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

    # handler for the 'git clone' command
    def handleCloneCommand(self, sender, arguments):
        """
        clone <targeturl> [<localname>]

        Clone a repository from target URL to local directory
        Use remote repository name if no local name is given
        """
        if len(arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(sender,
                "Usage: %s" % self._getDocForCurrentFunction())
            self.logger.debug("No URL for 'clone' provided.")
        else:
            # arguments given, the first one is treated as the URL
            repository = arguments[0]
            if len(arguments) >= 2:
                returnCode, localName = \
                    self._sanitizeArguments(sender,arguments[1])
            else:
                returnCode = 0
                localName = ""

            if returnCode == 0:
                self.printDebugMessage(sender, "Trying to clone from URL '%s'" % 
                    repository)

                commandPath = self.gitdir
                # execute git clone command and send result to sender
                returnCode, result = self.executeShellCommand(
                    "git clone %s %s" % (repository, localName), commandPath)
                if returnCode == 0:
                    self.sendMessage(sender, result)
                elif returnCode == 128:
                    self.sendMessage(sender, "Target directory already exists")
                else:
                    self.sendMessage(sender, "Cloning failed! Error %s" % returnCode)

