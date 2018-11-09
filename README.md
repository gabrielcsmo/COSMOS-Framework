COSMOS - Framework for Combining Simulation and Optimization Software

It has three main functions:
- optimize application input and parameters
- provide an optimal scheduling policy for all sub-tasks of the application
- analyze the application results.

Requirements:
- python2.7

Steps for using COSMOS with broker running on localhost:
- go to <b>task_examples/pi_computing</b> and compile a dummy program that computes pi in N iterations
- edit the configs/broker-config.json file and add:
   - at least one host
   - choose scheduling method (at this moment, only min-min is implemented)
   - set rootfs field to the folder where you have your application / scripts / input
   (in our case is /path/to/repo/task_examples/pi_computing)
- [Optional step] edit configs/optimizer-config.json and add optimization methods for each task.
You can have one <b>pre</b> optimization method that gets executed before the task is scheduled
and one <b>post</b> method that is executed after the task finishes execution.
- edit configs/tasks.json (in our case pi_tasks.json) and for each task specify:
  - command: this is what gets executed in the background thread
  - args: command arguments used when starting execution
  - priority: used when using the priority-scheduling method from broker config (not implemented yet)
  - length: estimated task length used when computing the load for selecting the host

- ./main.py --commands-file configs/pi_tasks.json

If you have any suggestions or ideas please feel free to contribute either by pull requests or
sending patch on email.
