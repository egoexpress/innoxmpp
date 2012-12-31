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
        super(GitBot, self).__init__()

        self.configoptions.addConfigOption(
            name="gitdir",
            value="CHANGEME",
            description="directory to store GIT clones")

        self.configoptions.addConfigOption(
            name="ghuser",
            value="CHANGEME",
            description="username for github.com")

        self.addRegExpCommandHandler("[(.*)].*pushed .+ new commit? to (.*)",
            self.handleGitHubPushMessage)

        # default repository when no parameter for repository
        # operations is provided
        self.defaultRepository = None

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
            commandPath = os.path.join(self.configoptions["gitdir"], repository)

            # check if path exists at all
            # don't reveal path in return message
            if not os.path.exists(commandPath):
                self.printDebugMessage(sender,
                    "No git clone with name '%s' exists" % repository)
                return 1, ""

            # check if constructed path is a valid git repository/clone
            if not os.path.exists(os.path.join(commandPath, ".git")):
                self.printDebugMessage(sender,
                    "'%s' is no GIT repository" % commandPath)
                return 1, ""

            return 0, commandPath

        return returnCode, ""

    def handleGitHubPushMessage(self, sender, repository, branch):
        """
        handle push message command from GitHub
        perform pull on given repository
        """
        self.handlePullCommand(None, [repository, ])

    # handler for the 'git commit -a [-m <message>]' command
    def handleCommitCommand(self, sender, arguments):
        """
        commit [<repository>] [<message>]

        Commit current state of <repository> using optional <message>
        """
        repository = None

        if len(arguments) == 0:
            # no arguments provided, send help (using __doc__) if no
            # default repository is set
            if self.defaultRepository == None:
                self.sendMessage(sender,
                    "Usage: %s" % self._getDocForCurrentFunction())
                self.printDebugMessage(sender, "No default repository set")
                return 2
            else:
                repository = self.defaultRepository
        else:
            repository = arguments[0]

        self.printDebugMessage(sender,
            "Trying to commit repository '%s'" % repository)

        returnCode = 0

        if len(arguments) > 1:
            commitMsg = ' '.join(arguments[1:]).strip('"')
            returnCode, commitMsg = self._sanitizeArguments(
                sender, commitMsg)
        else:
            commitMsg = "Autocommit using GitBot"

        # we can safely ignore the case when the returnCode was != 0
        # as an error message is sent by _sanitizeArguments
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
        pull [[<repository>] | [help]]

        Pull a directory from its origin
        """
        repository = None

        if len(arguments) == 0:
            if self.defaultRepository == None:
                self.sendMessage(sender,
                    "Usage: %s" % self._getDocForCurrentFunction())
                self.printDebugMessage(sender, "No default repository set")
                return 2
            else:
                repository = self.defaultRepository
        elif len(arguments) == 1 and arguments[0] == "help":
            # no arguments provided, send help (using __doc__)
            self.sendMessage(sender,
                "Usage: %s" % self._getDocForCurrentFunction())
            self.logger.debug("No repository name for 'pull' provided.")
            return 1

        # arguments given, the first one is treated as the repository
        # all other arguments are ignored (for now)
        if repository == None:
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
        push [<repository>]

        Push a given directory to its origin
        """
        if len(arguments) == 0:
            if self.defaultRepository == None:
                # no arguments provided and default repository not set
                # send help (using __doc__)
                self.sendMessage(sender,
                    "Usage: %s" % self._getDocForCurrentFunction())
                self.printDebugMessage("No repository name for 'push' provided.")
                return 2
            else:
                repository = self.defaultRepository
        elif len(arguments) == 1 and arguments[0] == "help":
                self.sendMessage(sender,
                    "Usage: %s" % self._getDocForCurrentFunction())
                return 1
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
            self.printDebugMessage("No URL for 'clone' provided.")
        else:
            # arguments given, the first one is treated as the URL
            targetURL = arguments[0]
            if len(arguments) >= 2:
                returnCode, localName = \
                    self._sanitizeArguments(sender, arguments[1])
            else:
                returnCode = 0
                localName = ""

            if returnCode == 0:
                self.printDebugMessage(sender, "Trying to clone from URL '%s'" %
                    targetURL)

                commandPath = self.configoptions["gitdir"]

                if not os.path.exists(commandPath):
                    self.printDebugMessage(sender,
                        "Target git directory doesn't exist, check your config!")
                    return 1, ""

                # execute git clone command and send result to sender
                returnCode, result = self.executeShellCommand(
                    "git clone %s %s" % (targetURL, localName), commandPath)
                if returnCode == 0:
                    self.sendMessage(sender, "%sCompleted successful!" % result)
                elif returnCode == 128:
                    self.sendMessage(sender, "Target cloning directory already exists")
                else:
                    self.sendMessage(sender, "Cloning failed! Error %s" %
                        returnCode)

    # handler for the 'git branch [-a]' command
    def handleBranchCommand(self, sender, arguments):
        """
        branch [<repository>] [<branchname>]

        Create <branchname> in <repository> (or list branches for <repository>)
        """
        branchname = None

        if len(arguments) == 0:
            if self.defaultRepository == None:
                # no arguments provided, send help (using __doc__)
                self.sendMessage(sender,
                    "Usage: %s" % self._getDocForCurrentFunction())
                self.printDebugMessage("No repository name for 'branch' provided.")
                return 2
            else:
                repository = self.defaultRepository
        elif len(arguments) == 1:
            if self.defaultRepository == None:
                repository = arguments[0]
            else:
                repository = self.defaultRepository
                branchname = arguments[0]
        else:
            repository = arguments[0]
            branchname = arguments[1]

        returnCode, commandPath = \
            self._getGitRepositoryPath(sender, repository)

        self.logger.debug("Repository path: %s" % commandPath)

        # repository name is valid
        if returnCode == 0:

            # branch name is not set - only list branches
            if branchname == None:

                self.printDebugMessage(sender,
                    "Listing branches of repository '%s'" % repository)

                # execute git branch command and send result to sender
                returnCode, result = self.executeShellCommand(
                    "git branch -a", commandPath)
            else:
                # get new branch name
                returnCode, branchname = self._sanitizeArguments(
                sender, branchname)

                if returnCode == 0:
                    self.printDebugMessage(sender,
                        "Creating branch '%s' in repository '%s'" %
                        (branchname, repository))

                    # execute git branch command and send result to sender
                    returnCode, result = self.executeShellCommand(
                        "git branch %s", (commandPath, branchname))

            if returnCode == 0:
                self.sendMessage(sender, result)

    # handler to set default repository
    def handleSetrepoCommand(self, sender, arguments):
        """
        setrepo <repository>

        Set default working repository for all following operations
        """
        if len(arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(sender,
                "Usage: %s" % self._getDocForCurrentFunction())
            self.logger.debug("No repository name to set as default provided.")

        # one parameter given - set as default repository
        elif len(arguments) == 1:
            repository = arguments[0]
            returnCode, commandPath = \
                self._getGitRepositoryPath(sender, repository)

            self.logger.debug("Repository path: %s" % commandPath)

            # repository name is valid
            if returnCode == 0:

                self.defaultRepository = repository

                self.printDebugMessage(sender,
                    "Setting default repository to '%s'" % repository)

    # handler to unset default repository
    def handleClearrepoCommand(self, sender, arguments):
        """
        clearrepo

        Unset default working repository for all following operations
        """
        if self.defaultRepository == None:
            self.printDebugMessage(sender,
                "No default repository set")
        else:
            oldRepo = self.defaultRepository
            self.defaultRepository = None

            self.printDebugMessage(sender,
                "Unset default repository, was '%s'" % oldRepo)

    # handler to change a branch in git using 'checkout'
    def handleCheckoutCommand(self, sender, arguments):
        """
        checkout [<repository>] <branch>

        Checkout given branch in repository
        """
        if len(arguments) == 0:
            # no arguments provided, send help (using __doc__)
            self.sendMessage(sender,
                "Usage: %s" % self._getDocForCurrentFunction())
            self.logger.debug("No repo and branch name provided.")
            return 1

        # one parameter  - branch if self.defaultRepository is set
        elif len(arguments) == 1:
            # default repository has not been set using 'setrepo'
            # deny operation
            if self.defaultRepository == None:
                self.sendMessage(sender,
                    "Usage: %s" % self._getDocForCurrentFunction())
                self.printDebugMessage(sender,
                    "No repository provided and default repo not set")
                return 1
            else:
                # default repository is set
                repository = self.defaultRepository
                branch = arguments[0]
        # two parameters (repository and branch) were provided
        else:
            repository = arguments[0]
            branch = arguments[1]

        # sanitize arguments
        returnCode, repository = self._sanitizeArguments(sender, repository)
        if returnCode == 0:
            returnCode, branch = self._sanitizeArguments(sender, branch)

        if returnCode == 0:
            # check if given repository is valid
            returnCode, commandPath = \
                self._getGitRepositoryPath(sender, repository)

            self.logger.debug("Repository path: %s" % commandPath)

            # repository name is valid, continue
            if returnCode == 0:

                # execute git checkout command to change branch
                returnCode, result = self.executeShellCommand(
                    "git checkout %s" % branch, commandPath)

                if returnCode == 0:
                    # branch change successful
                    self.sendMessage(sender, result)
                else:
                    # branch change failed (e.g. if branch doesn't exist)
                    self.sendMessage(sender,
                        "Checking out branch '%s' failed" % branch)

    # handler to list current local clones
    def handleListCommand(self, sender, arguments):
        """
        list

        List current local clones
        """
        directories = []

        gitPath = self.configoptions["gitdir"]
        if os.path.exists(gitPath):
            for directory in os.listdir(gitPath):
                pathDir = os.path.join(gitPath, directory)
                if os.path.exists(os.path.join(pathDir, ".git")):
                    directories.append(directory)

            self.sendMessage(sender, "Git clones:")
            self.sendMessage(sender, "\n".join(directories))
        else:
            self.sendMessage(sender,
                "Git directory doesn’t exist")
