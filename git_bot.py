#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    git_bot - startup script for the XMPP bot to control the git infrastructure
    Copyright (C) 2012 Bjoern Stierand
"""

from bots import GitBot

# create GitBot instance and run it
gitBot = GitBot.GitBot()
gitBot.run()