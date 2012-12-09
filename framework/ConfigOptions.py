# -*- coding: utf-8 -*-

"""
    Class to store config options for the bots
"""


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
        self.options[name]["value"] = value
