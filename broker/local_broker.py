#!/usr/bin/env python3
import signal
from lib.util import signal_handler
from lib.host import Host
import subprocess
import logging
from time import sleep
import os
import sys
import lib.info_server as info_server
from lib.qstat_parser import qstat_parse
from lib.common import InfoKeys
from threading import Thread, Event

signal.signal(signal.SIGINT, signal_handler)

class LocalBroker():
    # Any scheduling method that uses the monitoring service must be added here
    # You can also use this to monitor a scheduling method using the monitoring servicee, results are in performance.log
    SCHEDULE_USING_SYS_INFO = ["short-tasks", "mixed-tasks"]

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
        self.init_workspace()
        if self.scheduling_method in LocalBroker.SCHEDULE_USING_SYS_INFO:
            self.sys_info = info_server.SystemInfoServer()
        else:
            self.sys_info = None
        self.init_hosts()
        self.optimizer = optimizer

    def init_hosts(self):
        for hinfo in self.hosts_info:
            host = Host(hinfo, None)
            self.machines.append(host)
            if self.sys_info is not None:
                host.start_info_server(self.workspace)

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

        task.add_cmd_prefix()

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
    
    # this and schedule_tasks do the same thing, call the scheduling method for each task
    # what this function does on top of that is limit how many tasks are scheduled by the number of CPUS defined 
    # in the configuration of each machine
    def limited_schedule_tasks(self, tasks=[]):
        started_tasks = []
        done = Event()
        def monitor_started_tasks():
            nonlocal started_tasks
            while not done.is_set() or len(started_tasks) > 0:
                for task, host in started_tasks:
                    task.mark_if_finished()
                    if task.finished:
                        try:
                            started_tasks.remove((task, host))
                            host.task_completed(task)
                            if self.sys_info is not None:
                                self.sys_info.save_task_time(task)
                        except ValueError:
                            logging.error("[MonitorStartedTasks] Could not remove task '{}' from host '{}'".format(task.name, host.hostname))
                sleep(self.timeout)

        started_tasks_monitor = Thread(target=monitor_started_tasks)
        started_tasks_monitor.start()

        while len(tasks) > 0:
            task = tasks.pop(0)
            if task.is_ready(tasks):
                while not any(self.get_available_hosts()):
                    sleep(self.timeout)
                host = self.schedule_task(task)
                started_tasks.append((task, host))
        
        done.set()
        started_tasks_monitor.join()
                    
    def get_available_hosts(self):
        for host in self.machines:
            if not host.is_full():
                yield host

    def schedule_task(self, task):
        logging.info('\nScheduling task ' + task.to_string())
        # each task has its own folder in the workspace
        self.create_task_workspace(task)

        #call the preoptimize
        self.optimizer.pre_optimize_task(task)

        # mark task as not ready because you already scheduled it
        task.scheduled = True

        # now we are into the task folder
        if self.scheduling_method == 'min-min':
            return self.min_min_schedule(task)
        elif self.scheduling_method == 'work-queue':
            return self.work_queue_schedule(task)
        elif self.scheduling_method == 'max-min':
            return self.max_min_schedule(task)
        elif self.scheduling_method == 'long-tasks':
            return self.long_tasks_load_schedule(task)
        elif self.scheduling_method == 'short-tasks':
            return self.short_task_load_schedule(task)
        elif self.scheduling_method == 'mixed-tasks':
            return self.mixed_tasks_schedule(task)
        else:
            return self.priority_schedule(task)

    def min_min_schedule(self, task):
        mach_id = self.get_fastest_min_host(task)
        self.machines[mach_id].send_task(task)
        return self.machines[mach_id]

    def max_min_schedule(self, task):
        pass

    def work_queue_schedule(self, task):
        pass

    def priority_schedule(self, task):
        pass

    def short_task_load_schedule(self, task):
        best_machine, best_score = None, None
        current_usage = {}
        for host in self.get_available_hosts():
            usage = self.sys_info.get_usage(host.hostname)
            score = (100 - usage[InfoKeys.SYSTEM_CPU]) * task.cpu_weight + (100 - usage[InfoKeys.SYSTEM_MEMORY]) * task.memory_weight
            if best_machine is None or score > best_score:
                best_machine = host
                best_score = score

        # we receive usage stats periodically, so we add the estimated task length to the current score
        # so that if another task is scheduled before the usage is updated we won't end up
        # scheduling on the same best_machine (this is usually the case for the first scheduled tasks)
        self.sys_info.local_update_usage(best_machine.hostname, task)

        best_machine.send_task(task)
        return best_machine
    
    # uses 'qstat' to find information about the system
    # because qstat is not updated often, this policy yields best results with long tasks
    def long_tasks_load_schedule(self, task):
        best_machine = None
        all_machines_usage = [(host, qstat_parse(host.hostname)) for host in self.get_available_hosts()]
        all_machines_usage = list(filter(lambda elem: elem[1] is not None, all_machines_usage))

        if len(all_machines_usage) == 0:
            logging.warn("[long-tasks policy] Could not parse usage for any machine, defaulting to min-min policy.")
            return self.min_min_schedule(task)
        elif len(all_machines_usage) == 1:
            best_machine = all_machines_usage[0][0]
        else:
            best_score = None
            for host, usage in all_machines_usage:
                score = (100 - usage['np_load_avg']) * task.cpu_weight + (100 - usage['mem_used']) * task.memory_weight
                if best_machine is None or score > best_score:
                    best_machine, best_score = host, score
        
        logging.info("[long-tasks policy] Schedule on " + best_machine.hostname)
        best_machine.send_task(task)
        
        return best_machine
    
    def mixed_tasks_schedule(self, task):
        time_estimate = self.sys_info.get_task_time_estimate(task.name)
        # tasks that are 5 minutes or longer can be scheduled using qstat information
        if time_estimate is not None and time_estimate > 5*60:
            print(f"Long task detected: {task.name}")
            return self.long_tasks_load_schedule(task)
        else:
            return self.short_task_load_schedule(task)