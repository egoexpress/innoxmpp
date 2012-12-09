# -*- coding: utf-8 -*-

"""
    Class to store config options for the bots
"""

import configparser


class ConfigOptions():

    def __init__(self):
        """
        Designated initializer
        """
        self.options = {}

    def addConfigOption(self, name, value, description):
        """
        add option to config dictionary
        """
        self.options[name] = {
            "value": value,
            "description": description
        }

    def getConfigValue(self, name):
        """
        return value for config item
        """
        if name in self.options:
            return self.options[name]["value"]
        return None

    def __getitem__(self, name):
        """
        overload special method to provide direct access to items via dict
        syntax
        """
        return self.getConfigValue(name)

    def __setitem__(self, name, value):
        """
        overload special method to provide direct access to items via dict
        syntax
        """
        return self.setConfigValue(name, value)

    def setConfigValue(self, name, value):
        """
        overload special method to provide direct access to items via dict
        syntax
        """
        self.options[name]["value"] = value

    def processCommandLineArguments(self, arguments):
        """
        process arguments that came from the argumentparser
        """
        # replace default config options if any value is set
        for name, value in arguments.items():
            if value != None:
                self.setConfigValue(name, value)

    def parseConfig(self, classname, config):
        """
        process configparser arguments
        """
        for key in self.options.keys():
            try:
                value = config.get(classname, key)
                self.setConfigValue(key, value)
            except configparser.NoOptionError:
                # ignore options that are not set in the config file
                pass
