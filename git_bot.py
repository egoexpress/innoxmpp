#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    git_bot - startup script for the XMPP bot to control the git infrastructure
    Copyright (C) 2012 Bjoern Stierand
"""

from bots.GitBot import GitBot
from framework.BotRunner import BotRunner

# set up BotRunner and startup the bot
gitBot = BotRunner(GitBot)
gitBot.run()
