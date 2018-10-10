import sys
import os


class Optimizer(object):
    def __init__(self, optimizer_config):
        self.config = optimizer_config

    def pre_optimize_task(self, task):
        pass

    def post_optimize_task(self, task):
        pass

    def optimize(self):
        pass