# DESCRIPTION

Generate graphs from `pidstat` command output.


# REQUIREMENT

* Python
    *   Python v3.x
    *   libraries (You can install like this: `pip install numpy pandas matplotlib`)
        *   numpy
        *   pandas
        *   matplotlib


# HOW TO USE

For this script, `pidstat` command **MUST BE** run with `-hurdsw` options like as follows:
``` bash
$ pidstat -hurdsw -p <PID> 1 >pidstat.log
```

And then, generate graphs:
``` bash
$ python3 pidstat_analyzer.py <pidstat.log>
```


# GENERATED GRAPH EXAMPLES

### CPU Usage

![CPU Usage](./images/pidstat_cpu_usage.png)


### Disk I/O

![Disk I/O](./images/pidstat_disk_io.png)


### MEM Usage

![MEM Usage](./images/pidstat_mem_usage.png)


### Context Switch Count

![Proc Info](./images/pidstat_context_switch_counts.png)


### Page Fault Count

![Swapping](./images/pidstat_page_fault_counts.png)


### Stack size

![System Info](./images/pidstat_stack_size.png)
