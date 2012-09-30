# -*- coding: utf-8 -*-

"""
    BotRunner - a running class for innoxmpp bots
    Part of the InnoXMPP framework
    Copyright (C) 2012 Bjoern Stierand
"""

import argparse

class BotRunner():
	"""
	BotRunner - execute bots and handle command line input
	"""

	def __init__(self, botclass):
		"""
		Designated initializer
		"""
		self.botClass = botclass

		# instantiate bot class
		self.botInstance = botclass(configOptions)

		# set up argument parser
		self.parser = argparse.ArgumentParser()

		# add generic arguments
		self.parser.add_argument("--config", help="set alternate config file location")

	def run(self):
		"""
		run the bot instance
		"""
		self.arguments = parser.parse_args()
		self.botInstance.run(configoptions=self.arguments)
