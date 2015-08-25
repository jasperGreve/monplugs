#!/usr/bin/python

# check_snimpy.py - Check arbitrary snmp values using snimpy. Thresholds can be specified from the commandline

# Import PluginHelper and some utility constants from the Plugins module
from pynag.Plugins import PluginHelper,ok,warning,critical,unknown

# Import Snimpy
from snimpy.manager import Manager
from snimpy.manager import load

# Create an instance of PluginHelper()
helper = PluginHelper()

# Optionally, let helper handle command-line arguments for us for example --threshold
# Note: If your plugin needs any commandline arguments on its own (like --hostname) you should add them
# before this step with helper.parser.add_option()

helper.parser.add_option("-M", help="MIB File", dest="mib", default='IF-MIB')
helper.parser.add_option("-V", help="MIB Value", dest="value", default='')
helper.parser.add_option("-H", help="Hostname or IP", dest="host", default='localhost')
helper.parser.add_option("--Version", help="Snmp Version", dest="version", default='2')
helper.parser.add_option("-c", help="Snmp Comunity", dest="community", default='public')

helper.parse_arguments()


# Here starts our plugin specific logic. Lets try to read /proc/loadavg
# And if it fails, we exit immediately with UNKNOWN status
try:
    load(helper.options.mib)
except Exception, e:
    helper.exit(summary="Could not read MIB file.", long_output=str(e), exit_code=unknown, perfdata='')

m=Manager(helper.options.host,helper.options.community,int(helper.options.version))


formatstring=helper.options.value+': %s'
commandstring="m."+helper.options.value
content=eval(commandstring)
helper.add_summary(formatstring % content)


# Read metrics from /proc/loadavg and add them as performance metrics
#load1,load5,load15,processes,last_proc_id = content.split()
#running,total = processes.split('/')

# If we so desire we can set default thresholds by adding warn attribute here
# However we decide that there are no thresholds by default and they have to be
# applied on runtime with the --threshold option
helper.add_metric(label=helper.options.value,value=content)
#helper.add_metric(label='load5',value=load5)
#helper.add_metric(label='load15',value=load15)
#helper.add_metric(label='running_processes',value=running)
#helper.add_metric(label='total_processes',value=total)

# By default assume everything is ok. Any thresholds specified with --threshold can overwrite this status:
helper.status(ok)

# Here all metrics will be checked against thresholds that are either
# built-in or added via --threshold from the command-line
helper.check_all_metrics()

# Print out plugin information and exit nagios-style
helper.exit()
