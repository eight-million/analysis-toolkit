# DESCRIPTION

Generate graphs from `vmstat` command output.


# REQUIREMENT

* Python
    *   Python v3.x
    *   libraries (You can install like this: `pip install numpy pandas matplotlib`)
        *   numpy
        *   pandas
        *   matplotlib


# HOW TO USE

For this script, `vmstat` command **MUST BE** run with `-t` option like as follows:
``` bash
$ vmstat -t 1 >vmstat.log
```

And then, generate graphs:
``` bash
$ python3 vmstat_analyzer.py <vmstat.log>
```


# GENERATED GRAPH EXAMPLES

### CPU Usage

![CPU Usage](./images/vmstat_cpu_usage.png)


### Disk I/O

![Disk I/O](./images/vmstat_disk_io.png)


### MEM Usage

![MEM Usage](./images/vmstat_mem_usage.png)


### Process Info

![Proc Info](./images/vmstat_proc.png)


### Swapping

![Swapping](./images/vmstat_swapping.png)


### System Info

![System Info](./images/vmstat_system_info.png)
