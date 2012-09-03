#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    git_bot - startup script for the XMPP bot to control the git infrastructure
    Copyright (C) 2012 Bjoern Stierand
"""

from bots import GitBot
import sys
import logging

# force UTF8 encoding 
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

loglevel=logging.DEBUG

# Setup logging.
logging.basicConfig(level=loglevel,
                    format='%(levelname)-8s %(message)s')

gitBot = GitBot.GitBot()
gitBot.run()

