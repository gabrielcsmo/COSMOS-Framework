#!/usr/bin/env python3
import signal
import sys
import logging
from lib.host import Host
from lib.parameter import Parameter
from pydoc import locate

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

def try_converting_from_string(s):
    """
    tries to convert s to int, float or str
    and returns a tuple of (val, type)
    If it fails to convert, returns None
    """
    for type in ["int", "float", "str"]:
        try:
            v = locate(type)(s)
            return (v, type)
        except:
            continue

def str_to_param(s):
    """
    :param s: string that can be one of the 3:
            --name=val
            -name=val
            val

    :return: Parameter from string
    """

    if not s:
        print("Empty string")
        return None

    """--name[=val]"""
    if s.startswith("-"):
        start_idx = 1
        format = Parameter.EQ_FORMAT1

        if len(s) < 2:
            print("Cannot have single char - param")
            return None

        if s[1] == '-' and len(s) == 2:
            print("Cannot have only -- param")
            return None

        """gets here on --param=val"""
        if s[1] == '-':
            start_idx = 2
            format = Parameter.EQ_FORMAT2

        tokens = s[start_idx:].split("=")

        if len(tokens) == 1:
            return Parameter(name=tokens[0], value=tokens[0],
                             type="str", fmt=format)
        if len(tokens) > 2 or not tokens[1]:
            print("Parameter: {} is in the wrong format".format(s))
            return None
        else:
            t = try_converting_from_string(tokens[1])
            if not t:
                return None
            return Parameter(name=tokens[0], value=t[0],
                             type=t[1], fmt=format)
    else:
        t = try_converting_from_string(s)
        if not t:
            return None
        return Parameter(name=s, value=t[0],
                         type=t[1], fmt=Parameter.S_FORMAT)