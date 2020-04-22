from random import choice
import json

TESTS = [(100000000, 10), (500000000, 50), (1000000000, 100), (2000000000, 200)]

def crete_task():
    args, length = choice(TESTS)
    return {
        "dependencies" : [],
        "command" : "./pi",
        "args" : str(args),
        "priority" : 0,
        "length" : length
    }

OUTFILE = 'rand_pi_tasks.json'
NTASKS = 50

generated = {}
for i in range(0, NTASKS):
    generated[str(i)] = crete_task()

with open(OUTFILE, 'w') as f:
    json.dump(generated, f)