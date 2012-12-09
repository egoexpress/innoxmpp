#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    BackupBot - an XMPP bot to control the system backup performed by duplicity
    Copyright (C) 2012 Bjoern Stierand
"""

from bots.BackupBot import BackupBot
from framework.BotRunner import BotRunner

# create LinuxBot instance and run it
backupBot = BotRunner(BackupBot)
backupBot.run()
