import logging
import sys
import os
import json
from controller import Controller
from broker.broker import Broker
from optimizer.CorsikaOptimizer import CorsikaOptimizer
from optimizer.optimizer import Optimizer
from broker.task import create_tasks
from optimizer.Tools4LammpsOptimizer import T4l_optimizer


class T4lController(Controller):
    def __init__(self):
        super(T4lController, self).__init__()
        logging.info("Tools4Lamps controller created!")

    def parse_commands_file(self, commands_file=None):
        logging.info("Parse controller commands file")
        if commands_file == None:
            logging.warn("\tCommands file is missing")
            return
        try:
            tasks_dict = json.load(open(commands_file))
            self.tasks = create_tasks(tasks_dict)
            for task in self.tasks:
                logging.info(task.to_string())
        except Exception as e:
            logging.error("Error when parsing json config file:\n{}".format(e))
            sys.exit(1)

    def parse_controller_config(self, controller_config):
        logging.info("Parse controller config")
        if controller_config == None:
            logging.warn("\tParser Config not specified")
            return

    def parse_broker_config(self, broker_config):
        logging.info("Parse broker config: {}".format(broker_config))
        if broker_config == None:
            logging.warn("\tBroker Config not specified")
            return
        try:
            config_json = json.load(open(broker_config))
        except Exception as e:
            logging.error("Error when parsing json config file:\n{}".format(e))
            sys.exit(1)
        self.broker_config = config_json

    def parse_optimizer_config(self, optimizer_config):
        logging.info("Parse optimizer config:".format(optimizer_config))
        if optimizer_config == None:
            logging.warn("\tOptimizer Config not specified")
            return
        try:
            config_json = json.load(open(optimizer_config))
        except Exception as e:
            logging.error("Error when parsing json config file:\n\t" + str(e))
            sys.exit(1)
        self.optimizer_config = config_json

    def main_loop(self):
        #optimizer = T4l_optimizer(self.optimizer_config)
        optimizer = Optimizer(self.optimizer_config)
        broker = Broker(self.broker_config, optimizer)
        self.print_info()

        broker.schedule_tasks(self.tasks)