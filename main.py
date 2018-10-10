#!/usr/bin/env python3
import logging
from controller.tools4lammps_controller import T4l_controller
import argparse

logging.basicConfig(filename='engine.log', level=logging.INFO)

parser = argparse.ArgumentParser(description="Adaptive Parallel Execution Engine")
parser.add_argument('--config', action = "store", help = "Controller config file",
                    type = str, required = False)
parser.add_argument('--broker-config', action = "store", help = "Broker config file",
                    default="configs/broker-config.json", type = str, required = False)
parser.add_argument('--optimizer-config', action = "store", help = "Optimizer config file",
                    type = str, required = False)
parser.add_argument('--commands-file', action = "store", help = "Controller commands file",
                    type = str, required = False)

def main():
    args = parser.parse_args()
    cconfig = args.config
    bconfig = args.broker_config
    oconfig = args.optimizer_config
    commands_file = args.commands_file

    controller = T4l_controller()
    controller.parse_config(controller_config=cconfig,
                            optimizer_config=oconfig,
                            broker_config=bconfig)

    controller.parse_commands_file(commands_file)

    controller.main_loop()

if __name__ == '__main__':
    main()



