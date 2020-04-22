import subprocess
import sys
import logging

class Task():
    def __init__(self, id, task_dependencies = [],
                 propagate_ws = True, custom_rootfs = None, task_ws_id = None,
                 priority = 0,  length = 0,
                 command = "", args = ""):
        self.id = id
        self.task_dependencies = [str(i) for i in task_dependencies]
        if self.id in self.task_dependencies:
            logging.info("Task {0} is in its own dependencies: {1}".format(self.id,
                                                                    str(self.task_dependencies)))
            sys.exit(1)
        self.custom_rootfs = custom_rootfs
        self.propagate_workspace = propagate_ws
        self.task_folder = "task_" + str(self.id)
        self.finished = False
        self.ready = False
        self.qsub_id = None
        self.ws_task_id = task_ws_id
        self.priority = priority
        self.command = command
        self.args = args
        self.length = length
        self.scheduled = False
        self.already_pre_optimized = False
        self.already_post_optimized = False
        self.cpu_weight = 0.5
        self.memory_weight = 0.5
        """ if this task doesn't depend on any other task
            mark it as ready to be scheduled
        """
        if len(self.task_dependencies) == 0:
            self.ready = True
        self.background_thread = None
        # local or qsub
        self.task_type = None

    def to_string(self):
        rstr = ""
        rstr += "Task " + self.id + ": \n\t"
        rstr += "-> dependencies: " + str(self.task_dependencies) + "\n\t"
        rstr += "-> command: " + str(self.command) + "\n\t"
        rstr += "-> command args: " + str(self.args) + "\n\t"
        rstr += "-> length: " + str(self.length) + "\n\t"
        rstr += "-> priority: " + str(self.priority) + "\n\t"
        rstr += "-> finished: " + str(self.finished) + "\n\t"
        rstr += "-> ready: " + str(self.ready)
        return rstr

    def get_rootfs(self):
        """
        :return: str: either rootfs, either task_X if workspace depends
                    on the results present in workspace of task X
        """
        if not self.ws_task_id:
            return "rootfs"
        return "task_" + str(self.ws_task_id)

    def get_id(self):
        return self.id

    def get_length(self):
        return self.length

    def get_priority(self):
        return self.priority

    def get_command(self):
        return self.command

    def get_args(self):
        return self.args

    def set_qsub_id(self, qid):
        self.qsub_id = qid

    def is_ready(self, tasks):
        for task in tasks:
            if task.id in self.task_dependencies:
                if not task.is_finished():
                    logging.info("Task " + self.id + " has unmet dependencies: " + task.id)
                    return False
        self.ready = True
        return True

    def mark_if_finished(self):
        if self.task_type == 'local':
            self.mark_if_finished_local()
        elif self.task_type == 'qsub':
            self.mark_if_finished_qsub()

    def mark_if_finished_local(self):
        if not self.background_thread:
            logging.info("Background thread not set")
            return
        if self.finished:
            return
        self.finished = self.background_thread.is_finished()

    def mark_if_finished_qsub(self):
        """ if job doesn't have a qsub id it means the
            job wasn't scheduled yet (i.e. cannot be finished)
        """
        if not self.qsub_id:
            return
        """ if task was already marked as finished then
            exit here
        """
        if self.finished:
            return

        out = ""
        try:
            out = subprocess.check_output(['qstat']).decode('utf-8')
        except Exception as e:
            logging.info("Failed to check if job is active")

        """Search for qsub task id into active jobs"""
        lines = out.split("\n")
        finished = True
        for line in lines:
            if self.qsub_id in line:
                finished = False
        if finished:
            logging.info("Task " + self.qsub_id + " finished.")
            self.finished = True

    def set_background_thread(self, thr):
        self.background_thread = thr

    def set_type(self, t_type):
        self.task_type = t_type

    def is_finished(self):
        return self.finished

    def mark_ready(self):
        self.ready = True

    def already_scheduled(self):
        return self.scheduled



def create_tasks(tdic):
    """

    :rtype:
    """
    task_list = []
    for id in tdic:
        entry = tdic[id]
        crfs = None
        if "custom_rootfs" in entry:
            crfs = entry["custom_rootfs"]

        tdepid = None
        if "task_dependency_id" in entry:
            tdepid = entry["task_dependency_id"]
        try:
            t = Task(id=id, task_dependencies=entry["dependencies"], custom_rootfs=crfs,
                     task_ws_id=tdepid, priority=entry["priority"], length=entry["length"],
                     command=entry["command"], args=entry["args"])
            if 'cpu_weight' in entry and 'memory_weight' in entry:
                t.cpu_weight = entry['cpu_weight']
                t.memory_weight = entry['memory_weight']
            task_list.append(t)
        except Exception as e:
            logging.error(e)
    return task_list