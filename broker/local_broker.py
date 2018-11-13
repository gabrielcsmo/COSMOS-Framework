#!/usr/bin/env python3
import signal
from lib.util import signal_handler
from lib.host import Host
import subprocess
import logging
from time import sleep
import os
import sys

signal.signal(signal.SIGINT, signal_handler)

class LocalBroker():
    def __init__(self, config, optimizer):
        logging.info("Creating Local Broker Object")
        self.config = config
        self.scheduling_method = self.config['scheduling']
        self.hosts_info = self.config['hosts']
        self.rootfs = os.path.expanduser(self.config['rootfs'])
        self.workspace = os.path.expanduser(self.config['workspace'])
        self.propagate = bool(self.config["propagate_workspace"])
        self.timeout = int(self.config['timeout'])
        self.machines = []
        self.tasks = []
        self.job_num = 0
        # create hosts
        self.init_hosts()
        self.init_workspace()
        self.optimizer = optimizer


    def init_hosts(self):
        for hinfo in self.hosts_info:
            self.machines.append(Host(hinfo, None))

    def print_hosts(self):
        logging.info("\nHosts:")
        for machine in self.machines:
            logging.info(machine.to_string())

    def init_workspace(self):
        # remove the workspace if exists
        if os.path.exists(self.workspace):
            logging.info("Removing the workspace: {0}".format(self.workspace))
            os.system("rm -rf " + self.workspace)

        # create the workspace folder
        logging.info("Creating new workspace in: {0}".format(self.workspace))
        os.system("mkdir -p " + self.workspace)

        # archive the rootfs
        if not os.path.exists(self.rootfs):
            logging.error("Rootfs directory {0} is missing. Exiting now...".format(self.rootfs))
            sys.exit(1)

        # go into workspace and create an archieve with rootfs
        os.chdir(self.workspace)

        os.system("cp -rf " + self.rootfs + " rootfs")
        # save the rootfs into an archieve
        os.system("tar -zcf rootfs.tar.gz rootfs")

    def create_task_workspace(self, task):
        # go into workspace
        os.chdir(self.workspace)

        # remove the task folder if existing
        if os.path.exists(task.task_folder):
            os.system("rm -rf " + task.task_folder)

        # copy the rootfs in the task folder
        os.system("cp -rf " + task.get_rootfs() + " " + task.task_folder)
        os.chdir(task.task_folder)

    def copy_back_in_rootfs(self):
        os.chdir(self.workspace)
        task_folder = "task_" + str(self.job_num)
        logging.info("Copy the result back from {0}".format(task_folder))
        os.system("cp -rf " + task_folder + " rootfs")

    def get_fastest_min_host(self, task):
        ret_val = None
        ret_host = None
        for i in range(len(self.machines)):
            host = self.machines[i]
            if ret_val == None:
                ret_val = host.get_expected_load(task)
                ret_host = i
            elif host.get_expected_load(task) < ret_val:
                ret_val = host.get_expected_load(task)
                ret_host = i
        logging.info("\ton fastest host {0} - {1}".format(ret_val, self.machines[ret_host].to_string()))
        return ret_host

    def schedule_tasks(self, tasks=[]):
        self.tasks = tasks
        left = len(tasks)
        exit = False
        while not exit:
            t = tasks.pop(0)
            # mark it if already finished
            t.mark_if_finished()
            left -= 1
            if not t.already_scheduled() and t.is_ready(tasks):
                self.schedule_task(t)
            tasks.append(t)

            # iterate through all of the left tasks
            if left == 0:
                left = len(tasks)
                exit = True
                for task in tasks:
                    task.mark_if_finished()
                    if not task.is_finished():
                        exit = False
                    else:
                        self.optimizer.post_optimize_task(task)
                sleep(self.timeout)

    def schedule_task(self, task):
        logging.info('\nScheduling task ' + task.to_string())
        # each task has its own folder in the workspace
        self.create_task_workspace(task)

        #call the preoptimize
        self.optimizer.pre_optimize_task(task)

        # now we are into the task folder
        if self.scheduling_method == 'min-min':
            self.min_min_schedule(task)
        elif self.scheduling_method == 'work-queue':
            self.work_queue_schedule(task)
        elif self.scheduling_method == 'max-min':
            self.max_min_schedule(task)
        else:
            self.priority_schedule(task)

        # mark task as not ready because you already scheduled it
        task.scheduled = True

    def min_min_schedule(self, task):
        mach_id = self.get_fastest_min_host(task)
        self.machines[mach_id].send_task(task)

    def max_min_schedule(self, task):
        pass

    def work_queue_schedule(self, task):
        pass

    def priority_schedule(self, task):
        pass