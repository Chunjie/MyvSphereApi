#!/usr/bin/env python

from pysphere import VIServer

server = VIServer()
server.connect("my.esx.host.example.org", "username", "secret")

datacenters = server.get_datacenters()  
for k,v in datacenters.items():
  print "key:" + k + ",value:" + str(v)

clusters = server.get_clusters()
for k,v in clusters.items():
  print "key:" + k + ",value:" + str(v)

# datacenter is case-senstive
hostlist = server.get_hosts()
for host in hostlist:
  print host

vmlist = server.get_registered_vms(datacenter="dev")
for vm_path in vmlist[:2]:
  vm = server.get_vm_by_path(vm_path)
  status = vm.get_status()
  print vm.properties
  print "vm_path=[%s], status=[%s]" % (vm_path, status)

server.disconnect()
