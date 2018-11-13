import logging

class Controller(object):
    def __init__(self):
        logging.info("Creating the Controller...")
        self.controller_config = None
        self.optimizer_config = None
        self.broker_config = None
        self.commands = {}  # (line_occured, command)

    def parse_config(self, controller_config=None, optimizer_config=None, broker_config=None):
        self.parse_controller_config(controller_config)
        self.parse_broker_config(broker_config)
        self.parse_optimizer_config(optimizer_config)

    def print_info(self):
        logging.info("\nGeneral Config:\n{}".format(self.controller_config))
        logging.info("\nBroker Config:\n{}".format(self.broker_config))
        logging.info("\nOptimizer Config:\n{}".format(self.optimizer_config))

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