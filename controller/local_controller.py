import logging
import sys
import os
import json
from controller import Controller
from broker.local_broker import LocalBroker
from optimizer.optimizer import Optimizer
from broker.task import create_tasks

class LocalController(Controller):
    def __init__(self):
        super(LocalController, self).__init__()
        print "Local controller created!"

    def parse_commands_file(self, commands_file=None):
        print "Parse controller commands file"
        if commands_file == None:
            print "\tCommands file is missing"
            return
        try:
            tasks_dict = json.load(open(commands_file))
            self.tasks = create_tasks(tasks_dict)
            for task in self.tasks:
                print task.to_string()
        except Exception as e:
            print "Error when parsing json config file:\n\t", e
            sys.exit(1)

    def parse_controller_config(self, controller_config):
        print "Parse controller config"
        if controller_config == None:
            print "\tParser Config not specified"
            return

    def parse_broker_config(self, broker_config):
        print "Parse broker config:", broker_config
        if broker_config == None:
            print "\tBroker Config not specified"
            return
        try:
            config_json = json.load(open(broker_config))
        except Exception as e:
            print "Error when parsing json config file:\n\t", e
            sys.exit(1)
        self.broker_config = config_json

    def parse_optimizer_config(self, optimizer_config):
        print "Parse optimizer config:", optimizer_config
        if optimizer_config == None:
            print "\tOptimizer Config not specified"
            return
        try:
            config_json = json.load(open(optimizer_config))
        except Exception as e:
            print("Error when parsing json config file:\n\t" + str(e))
            sys.exit(1)
        self.optimizer_config = config_json

    def main_loop(self):
        optimizer = Optimizer(self.optimizer_config)
        broker = LocalBroker(self.broker_config, optimizer)
        self.print_info()

        broker.schedule_tasks(self.tasks)
        """
        for task in self.commands["tasks"]:
            broker.schedule_task(task, blocking=True)
        optimizer = CorsikaOptimizer(self.optimizer_config)
        optimized_params = optimizer.optimize()

        # broker.schedule(optimized_params)
        """