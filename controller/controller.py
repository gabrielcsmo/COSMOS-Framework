import logging

class Controller(object):
    def __init__(self):
        print "Creating the Controller..."
        self.controller_config = None
        self.optimizer_config = None
        self.broker_config = None
        self.commands = {}  # (line_occured, command)

    def parse_config(self, controller_config=None, optimizer_config=None, broker_config=None):
        self.parse_controller_config(controller_config)
        self.parse_broker_config(broker_config)
        self.parse_optimizer_config(optimizer_config)

    def print_info(self):
        print "\nGeneral Config:\n", self.controller_config
        print "\nBroker Config:\n", self.broker_config
        print "\nOptimizer Config:\n", self.optimizer_config
        #print "\nCommands:\n", self.commands

    def parse_commands_file(self, commands_file):
        pass

    def parse_controller_config(self, controller_config):
        pass

    def parse_broker_config(self, broker_config):
        pass

    def parse_optimizer_config(self, optimizer_config):
        pass

    def main_loop(self):
        pass