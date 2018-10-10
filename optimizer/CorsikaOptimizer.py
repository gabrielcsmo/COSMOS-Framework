import sys
import os
import logging
from optimizer import Optimizer

class CorsikaOptimizer(Optimizer):
	def __init__(self, params):
		self.params = params
		self.task = params["tasks"][0]
		self.simlist = self.task["input"].split(',')[0]
		self.runfile = self.task["input"].split(',')[1]
		self.reasfile = self.task["input"].split(',')[2]
		self.available_cores = 0
		self.optimized_params = None
		# Sum up all available cores
		for host in params["hosts"]:
			self.available_cores += host["cpus"]

	def optimize(self):
		sim_f = None
		simf_lines = []
		run_f = None
		runf_lines = []
		logging.info("Available cores: " + str(self.available_cores))
		tasks = []
		sim_basename = os.path.dirname(self.simlist)
		run_basename = os.path.dirname(self.runfile)
		reas_basename = os.path.dirname(self.reasfile)
		new_simfiles = []
		new_runfiles = []
		new_reasfiles = []
		# Open SIM0000X.list and RUN0000X.inp SIM0000x.reas
		try:
			sim_f = open(self.simlist, "r")
			simf_lines = sim_f.readlines()
			run_f = open(self.runfile, "r")
			runf_lines = run_f.readlines()
			reas_f = open(self.reasfile, "r")
			reasf_lines = reas_f.readlines()
		except Exception as e:
			print(e)
			sys.exit(-1)

		# Try to split the Antennas SIMx.list file into 
		# maximum available_cores subfiles
		num_files = min(self.available_cores, len(simf_lines))
		for i in range(num_files):
			path = os.path.join(sim_basename, "SIM00000" + str(i + 1) + "_coreas").replace("/home/gabrielcsmo", "~")
			tasks.append({	"id": i + 1,
				  	"priority" : 10,
					"length" : 50,
					"command" : "~/start_corsika.sh task" + str(i) + " RUN00000" + str(i + 1) + ".inp",
					"output_file" : path})
			sim_fx = os.path.join(sim_basename, "SIM00000" + str(i + 1) + ".list")
			new_simfiles.append(open(sim_fx, "w"))
			
			reas_fx = os.path.join(reas_basename, "SIM00000" + str(i + 1) + ".reas")
			new_reasfiles.append(open(reas_fx, "w"))

			run_fx = os.path.join(run_basename, "RUN00000" + str(i + 1) + ".inp")
			new_runfiles.append(open(run_fx, "w"))

		for i in range(len(simf_lines)):
			new_simfiles[i % num_files].write(simf_lines[i])

		for i in range(num_files):
			for j in range(len(reasf_lines) - 1):
				new_reasfiles[i].write(reasf_lines[j])
			new_reasfiles[i].write('CorsikaParameterFile = ' + 'RUN00000' + str(i + 1) + '.inp\n')

		for i in range(num_files):
			new_runfiles[i].write('RUNNR	00000' + str(i + 1) + '\n')
			for j in range(1, len(runf_lines)):
				new_runfiles[i].write(runf_lines[j])

		# Close all subfiles
		for i in range(len(new_simfiles)):
			new_simfiles[i].close()
			new_runfiles[i].close()
			new_reasfiles[i].close()
		for task in tasks:
			print(task)
		self.params['tasks'] = tasks
		self.optimized_params = self.params
		return self.params
