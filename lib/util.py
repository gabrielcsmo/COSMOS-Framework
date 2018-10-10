#!/usr/bin/env python3
import signal
import sys
import logging
from lib.host import Host

def signal_handler(signal, frame):
	logging.info('You pressed Ctrl+C. I will exit now...')
	sys.exit(0)

def list_tasks(tasks):
	pstr = "Tasks to run:\n"
	for proc in tasks:
		pstr += "\t " + str(proc) + "\n"
	logging.info(pstr)

def init_hosts(args):
	hosts = args['hosts']
	output_folder = args['output_folder']
	logging.info("Initializing host info")
	ret_hosts = []
	for host_info in hosts:
		host_info['output_folder'] = output_folder
		ret_hosts.append(Host(host_info, args['pre-req']))
	return ret_hosts
