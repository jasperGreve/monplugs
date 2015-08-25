#!/usr/bin/python

# check_snimpy.py - Check arbitrary snmp values using snimpy. Thresholds can be specified from the commandline

# Import PluginHelper and some utility constants from the Plugins module
from pynag.Plugins import PluginHelper,ok,warning,critical,unknown

# Import Snimpy
from snimpy.manager import Manager
from snimpy.manager import load

import re
import memcache
import time


# Create an instance of PluginHelper()
helper = PluginHelper()

# Optionally, let helper handle command-line arguments for us for example --threshold
# Note: If your plugin needs any commandline arguments on its own (like --hostname) you should add them
# before this step with helper.parser.add_option()

helper.parser.add_option("-n", help="Interface name (regex)", dest="name", default='.')
helper.parser.add_option("-H", help="Hostname or IP", dest="host", default='localhost')
helper.parser.add_option("--Version", help="Snmp Version", dest="version", default='2')
helper.parser.add_option("-c", help="Snmp Comunity", dest="community", default='public')

helper.parse_arguments()


# Here starts our plugin specific logic. Lets try to read /proc/loadavg
# And if it fails, we exit immediately with UNKNOWN status
try:
    load('IF-MIB')
except Exception, e:
    helper.exit(summary="Could not read MIB file.", long_output=str(e), exit_code=unknown, perfdata='')

m=Manager(helper.options.host,helper.options.community,int(helper.options.version))
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
p = re.compile(helper.options.name)

values=['ifInOctets','ifOutOctets','ifInErrors','ifOutErrors','ifInUcastPkts','ifOutUcastPkts']

for interfaceKey in m.ifIndex:
    if p.search(str(m.ifDescr[interfaceKey])):
        for valuesKey in values:
            now=time.time()
            commandstr='m.'+valuesKey+"[%s]" % interfaceKey
            labelstr=str(m.ifDescr[interfaceKey])+'-'+valuesKey
            counthash=str(hash('checkinterfaces'+helper.options.host+labelstr))
            timehash=str(hash('now'+helper.options.host+labelstr))
            oldcounter=mc.get(str(counthash))
            oldtime=mc.get(str(timehash))
            if oldcounter is None:
                oldcounter = 0
            if oldtime is None:
                oldtime = now-30
            counter=eval(commandstr)
            mc.set(counthash,counter)
            mc.set(timehash, now)
            mbps=((counter-oldcounter)*(8))/(now-oldtime)
            #mbps=((counter-oldcounter)*(8/1000000))/(now-oldtime)
            
            helper.add_metric(label=labelstr, value=mbps)
            # print " %s: %i" % (labelstr, counter)


# By default assume everything is ok. Any thresholds specified with --threshold can overwrite this status:
helper.status(ok)

# Here all metrics will be checked against thresholds that are either
# built-in or added via --threshold from the command-line
helper.check_all_metrics()

# Print out plugin information and exit nagios-style
helper.exit()
