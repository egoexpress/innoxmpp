innoxmpp
========

Python XMPP admin 'bots' based on the SleekXMPP library

**Requirements:**

* [Python](http://www.python.org) >= 3.2.3 (Python2 is not supported)
* [SleekXMPP](http://sleekxmpp.com/)
* [DNSPython3](http://www.dnspython.com/)

**Using Packages:**

The development was done with the Git versions of both SleekXMPP and DNSPython3.
Tests on Debian Sid (as of Sep 6th 2012) showed that the current packaged version
of SleekXMPP (python3-sleekxmpp: 1.0~beta5-2) throws an error when starting a bot.

    DEBUG     ==== TRANSITION disconnected -> connected
    Traceback (most recent call last):
      File "git_bot.py", line 13, in <module>
        gitBot.run()    
      File "/home/wonder/scripts/innoxmpp/bots/GenericBot.py", line 109, in run
        self.process(block=True)
      File "/usr/lib/python3/dist-packages/sleekxmpp/basexmpp.py", line 148, in process
        return XMLStream.process(self, *args, **kwargs)
    TypeError: process() got an unexpected keyword argument 'block'

Using the latest version from the (cloned) [Git repository](https://github.com/egoexpress/SleekXMPP) didn't show this behaviour.

**Getting the code:**

The code of this project is available at GitHub at <https://github.com/egoexpress/innoxmpp>