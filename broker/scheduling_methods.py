import logging
from lib.util import list_tasks
from lib.util import init_hosts


def get_fastest_min_host(hosts, task):
    ret_val = None
    ret_host = None
    for i in range(len(hosts)):
        host = hosts[i]
        if ret_val == None:
            ret_val = host.get_expected_load(task)
            ret_host = i
        elif host.get_expected_load(task) < ret_val:
            ret_val = host.get_expected_load(task)
            ret_host = i
    print("fastest host {0} - {1}".format(ret_val, hosts[ret_host].to_string()))
    return ret_host


def min_min_schedule(args):
    logging.info("Using Min-Min Schedule")
    hosts = init_hosts(args)
    for host in hosts:
        logging.info(host.to_string())
    list_tasks(args['tasks'])
    for task in args['tasks']:
        host_id = get_fastest_min_host(hosts, task)
        hosts[host_id].send_task(task)
    for host in hosts:
        host.tasks_join()


def max_min_schedule(args):
    logging.info("Using Max-Min Schedule")
    pass


def work_queue_schedule(args):
    logging.info("Using Work-Queue Schedule")
    pass


def priority_schedule(args):
    logging.info("Using Priority Schedule")
    pass
