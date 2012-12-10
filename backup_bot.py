#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    BackupBot - an XMPP bot to control the system backup performed by duplicity
    Copyright (C) 2012 Bjoern Stierand
"""

from bots import BackupBot

backupBot = BackupBot.BackupBot()
backupBot.run()
