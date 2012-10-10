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
        self._loadConfigSettings()

    # load ini settings from config file innoxmpp.ini's [GitBot] section
    def _loadConfigSettings(self):
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
    def _sanitizeArguments(self, sender, textArgument):
        """
        Sanitize input, reject if it contains suspicious characters
        that could lead to execution of arbitrary shell commands
        """
        errorMsg = ""

        # return error code if it contains ";" or "&"
        if textArgument.find("&") != -1 or textArgument.find(";") != -1:
            errorMsg = "ERROR: Invalid character found in argument"

        # if an error occurred (that is, an error msg is set, return 1
        if errorMsg != "":
            self.sendMessage(sender, errorMsg)
            return 1, errorMsg

        # no error occurred, return 0 and the input argument
        return 0, textArgument

    # construct fully qualified repository path for given _repository
    # plus some sanity checks (e.g. if the dir is a valid repository)
    def _getGitRepositoryPath(self, sender, repository):
        """
        create fully qualified name for repository using the
        ini setting 'gitdir', send error messages to sender
        """

        # sanitize repository name input (just to make sure nothing
        # gets somehow messed up by strange control characters)
        returnCode, repositoryPath = self._sanitizeArguments(sender, \
            repository)

        if returnCode == 0:

            # create fully qualified path
            commandPath = os.path.join(self.gitdir, repository)

            # check if path exists at all
            # don't reveal path in return message
            if not os.path.exists(commandPath):
                self.printDebugMessage(sender, 
                    "No git clone with name '%s' exists" % repository)
                return 1, ""

            # check if constructed path is a valid git repository/clone
            if not os.path.exists(os.path.join(commandPath,".git")):
                self.printDebugMessage(sender, 
                    "'%s' is no GIT repository" % commandPath)
                return 1, ""

            return 0, commandPath

        return returnCode, ""

    # handler for the 'git commit -a [-m <message>]' command
    def handleCommitCommand(self, sender, arguments):
        """
        commit <repository> [<message>]

        Commit current state of <repository> using optional <message>
        """
        if len(arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(sender,
                "Usage: %s" % self._getDocForCurrentFunction())
            self.logger.debug("No repository name for 'commit' provided.")
        else:
            repository = arguments[0]
            self.printDebugMessage(sender, 
                "Trying to commit repository '%s'" % repository)

            returnCode = 0

            if len(arguments) > 1:
                commitMsg = ' '.join(arguments[1:])
                returnCode, commitMsg = self._sanitizeArguments(
                    sender, commitMsg)
            else:
                commitMsg = "Autocommit using GitBot"

            # we can safely ignore the case when the returnCode was != 0
            # as an error message is sent my _sanitizeArguments
            if returnCode == 0:
                returnCode, commandPath = \
                    self._getGitRepositoryPath(sender, repository)
                if returnCode == 0:
                    # execute git commit command and send result to sender
                    returnCode, result = \
                        self.executeShellCommand(
                            "git commit -a -m \"%s\"" % commitMsg, 
                            commandPath)
                    if returnCode == 0:
                        self.sendMessage(sender, result)
                    elif returnCode == 1:
                        self.sendMessage(sender, "Nothing to commit")

    # handler for the 'git pull' command
    def handlePullCommand(self, sender, arguments):
        """
        pull <repository>

        Pull a directory from its origin
        """
        if len(arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(sender,
                "Usage: %s", self._getDocForCurrentFunction())
            self.logger.debug("No repository name for 'pull' provided.")
        else:
            # arguments given, the first one is treated as the repository
            # all other arguments are ignored (for now)
            repository = arguments[0]
            self.printDebugMessage(sender, "Trying to pull repository '%s'" % 
                repository)

            returnCode, commandPath = self._getGitRepositoryPath(sender, 
                repository)
            if returnCode == 0:
                # execute git pull command and send result to sender
                returnCode, result = self.executeShellCommand("git pull", 
                    commandPath)
                if returnCode == 0:
                    self.sendMessage(sender, result)

    # handler for the 'git push' command
    def handlePushCommand(self, sender, arguments):
        """
        push <repository>

        Push a given directory to its origin"
        """
        if len(arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(sender,
                "Usage: %s" % self._getDocForCurrentFunction())
            self.logger.debug("No repository name for 'push' provided.")
        else:
            # arguments given, the first one is treated as the repository
            # all other arguments are ignored (for now)
            repository = arguments[0]
            self.printDebugMessage(sender, "Trying to push repository '%s'" % 
                repository)

            returnCode, commandPath = self._getGitRepositoryPath(sender, 
                repository)
            if returnCode == 0:
                # execute git push command and send result to sender
                returnCode, result = self.executeShellCommand("git push", 
                    commandPath)
                if returnCode == 0:
                    self.sendMessage(sender, result)

    # handler for the 'git clone' command
    def handleCloneCommand(self, sender, arguments):
        """
        clone <targeturl> [<localname>]

        Clone a repository from target URL to local directory (or <localname>)
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
                    self.sendMessage(sender, "Cloning failed! Error %s" % 
                        returnCode)

    # handler for the 'git branch -a' command
    def handleBranchCommand(self, sender, arguments):
        """
        branch <repository> [<branchname>]

        Create <branchname> in <repository> (or list branches for <repository>)
        """
        if len(arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(sender,
                "Usage: %s" % self._getDocForCurrentFunction())
            self.logger.debug("No repository name for 'branch' provided.")
       
        # at least one paramter given - check for repository
        elif len(arguments) >= 1:
            repository = arguments[0]
            returnCode, commandPath = \
                self._getGitRepositoryPath(sender, repository)

            self.logger.debug("Repository path: %s" % commandPath)

            # repository name is valid
            if returnCode == 0:

                # only one argument - list branches
                if len(arguments) == 1:

                    self.printDebugMessage(sender, 
                        "Listing branches of repository '%s'" % repository)

                    # execute git branch command and send result to sender
                    returnCode, result = self.executeShellCommand(
                        "git branch -a", commandPath)
                else:
                    # get new branch name
                    returnCode, branchname = self._sanitizeArguments(
                    sender, arguments[1])

                    if returnCode == 0:
                        self.printDebugMessage(sender, 
                            "Creating branch '%s' in repository '%s'" % 
                            (branchname, repository))

                        # execute git branch command and send result to sender
                        returnCode, result = self.executeShellCommand(
                            "git branch %s", (commandPath, branchname))

                if returnCode == 0:
                    self.sendMessage(sender, result)
