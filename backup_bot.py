#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    BackupBot - an XMPP bot to control the system backup performed by duplicity
    Copyright (C) 2012 Bjoern Stierand
"""

from bots import BackupBot
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

backupBot = BackupBot.BackupBot()
backupBot.run()

