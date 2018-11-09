import logging
import sys
import os
import subprocess
from multiprocessing import Process
import threading


def exec_func(**kwargs):
    logging.info("Executing task: " + str(kwargs))
    task = kwargs['task']
    host = kwargs['host']
    destination = host['ip']

    if host['hostname'] != '':
        destination = host['hostname']
    if destination == '':
        logging.error('IP / Hostname is missing')
        sys.exit(1)

    ssh_command = "ssh -q " + host['user'] \
                  + "@" + destination \
                  + " \"" + task['command'] + "\""
    logging.info(ssh_command)
    os.system(ssh_command)

    scp_command = "scp -q " + host['user'] \
                  + "@" + destination \
                  + ":" + task['output_file'] \
                  + " " + os.path.join(host['output_folder'], str(task['id'])) \
        # os.system(scp_command)
    logging.info(scp_command)


class BackgroundThread(object):
    def __init__(self, command):
        self.command = format(command.strip())
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        os.system('./{}'.format(self.command))

    def is_finished(self):
        command = ['ps', '-ux']
        out = subprocess.check_output(command)
        if self.command in out:
            return False
        return True

class Host():
    def __init__(self, args, prereq):
        self.raw_args = args
        print(self.raw_args)
        self.hostname = args['hostname']
        self.ip = args['ip']
        self.cpus = args['cpus']
        self.used_cpus = 0
        self.processing_power = self.cpus * args['gflops']
        self.user = args['user']
        self.type = args['type']
        self.running_tasks = {}
        self.load = 0
        self.prereq = prereq
        self.do_prereq()
        self.cnt = 123

    def do_prereq(self):
        if self.prereq == None:
            return
        for command in self.prereq:
            # execute scp command
            if command.startswith("scp"):
                c = command.replace("user", self.user)
                c = c.replace("hostname", self.hostname)
                print(c)
                os.system(c)

    def qsub_exec(self, task):
        out = None
        try:
            command = ["qsub", "-q", str(self.hostname), "-cwd", task.get_command()]
            out = subprocess.check_output(command)
        except Exception as e:
            print "Failed to submit job:", e
            return None
        print out
        # Output is like:
        # Your job 994012 ("run.sh") has been submitted
        tokens = out.split(" ")
        task.set_qsub_id(tokens[2])

    def local_exec(self, task):
        try:
            """create a script where to write command so we can identify
            it later with ps - required to see if task finished"""
            script_name = '_'.join([self.hostname, 'task', task.id]).replace(' ', '')

            """write the full command in the script and make it exec"""
            full_cmd = ' '.join([task.get_command(), task.get_args()])


            os.system('echo -e "#!/bin/sh\n{}" > {} && chmod +x {}'.format(full_cmd,
                                                                           script_name,
                                                                           script_name))
            task.set_background_thread(BackgroundThread(script_name))

        except Exception as e:
            print "Failed to execute job:", e

    def exec_task(self, task):
        if self.type == 'local':
            self.local_exec(task)
        elif self.type == 'qsub':
            self.qsub_exec(task)
        else:
            print "Unknown host type: {}".format(self.type)
            sys.exit(1)

    def send_task(self, task):
        """
        Keep a log of how many tasks are currently running on each host.
        Only scheduler have access to Hosts and access should not be
        concurrent.
        This should be called when a process starts on a host.
        """
        length = task.get_length()
        self.used_cpus += 1
        self.load += length
        task.set_type(self.type)

        self.exec_task(task)

        self.running_tasks[task.get_id()] = task
        print '\tTask: {0} is running now running\n'.format(task.get_id())

    def tasks_join(self):
        for task in self.running_tasks:
            task.join()

    def task_completed(self, task):
        '''
        Access should not be concurrent.
        This should be called when a process joins
        '''
        self.used_cpus -= 1
        self.load -= task['length']
        #self.running_tasks.remove(task)

    def to_string(self):
        res = ""
        res += "(" + self.ip + " <" + self.user + "@" + self.hostname + ">, "
        res += str(self.used_cpus) + "/" + str(self.cpus) + ", "
        res += str(self.load) + ")"
        return res

    def get_expected_load(self, task):
        """
		See what is the expected load if you schedule
		the task to this machine.
		ret_load = (actual_load + task_length) / processing_power
		"""
        ret = float(self.load + task.get_length()) / float(self.processing_power)
        return ret
