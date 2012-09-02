#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    BackupBot - an XMPP bot to control the system backup performed by duplicity
    Copyright (C) 2012 Bjoern Stierand
"""

import sys
import logging
import getpass
import ConfigParser

from bots import BackupBot

# force UTF8 encoding 
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


if __name__ == '__main__':

    loglevel=logging.DEBUG

    # Setup logging.
    logging.basicConfig(level=loglevel,
                        format='%(levelname)-8s %(message)s')

    xmpp = BackupBot.BackupBot()
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
