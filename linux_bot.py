#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    linux_bot - startup script for the XMPP bot to control a Linux box
    Copyright (C) 2012 Bjoern Stierand
"""

from bots import LinuxBot

# create LinuxBot instance and run it
linuxBot = LinuxBot.LinuxBot()
linuxBot.run()