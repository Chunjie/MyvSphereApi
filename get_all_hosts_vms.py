#!/usr/bin/env python

"""
Python program for listing the vms on an ESX / vCenter host
"""

#from __future__ import print_function

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import argparse
import atexit
import getpass

def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(
       description='Process args for retrieving all the Virtual Machines')
   parser.add_argument('-s', '--host', required=True, action='store',
                       help='Remote host to connect to')
   parser.add_argument('-o', '--port', type=int, default=443, action='store',
                       help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store',
                       help='User name to use when connecting to host')
   parser.add_argument('-p', '--password', required=False, action='store',
                       help='Password to use when connecting to host')
   args = parser.parse_args()
   return args


def PrintVmInfo(vm, depth=1):
   """
   Print information for a particular virtual machine or recurse into a folder
   or vApp with depth protection
   """
   maxdepth = 10

   # if this is a group it will have children. if it does, recurse into them
   # and then return
   if hasattr(vm, 'childEntity'):
      if depth > maxdepth:
         return
      vmList = vm.childEntity
      for c in vmList:
         PrintVmInfo(c, depth+1)
      return

   # if this is a vApp, it likely contains child VMs
   # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
   if isinstance(vm, vim.VirtualApp):
      vmList = vm.vm
      for c in vmList:
         PrintVmInfo(c, depth + 1)
      return

   summary = vm.summary
   #print summary
   print("Name              : ", summary.config.name)
   print("Path              : ", summary.config.vmPathName)
   print("Guest             : ", summary.config.guestFullName)
   print("UUID              : ", summary.config.uuid)
   print("Instance UUID     : ", summary.config.instanceUuid)
   annotation = summary.config.annotation
   if annotation != None and annotation != "":
      print("Annotation        : ", annotation)
   print("State             : ", summary.runtime.powerState)
   if summary.guest != None:
      ip = summary.guest.ipAddress
      if ip != None and ip != "":
         print("IP                : ", ip)
   if summary.runtime.question != None:
      print("Question  : ", summary.runtime.question.text)
   print("")


def PrintHostInfo(host):
   """
   Print information for a ESXi host.

   TODO: cluster
   """
   print host.host
   print host.name
   print host.summary
   print host.network


def main():
   """
   Simple command-line program for listing the virtual machines on a system.
   """

   args = GetArgs()
   if args.password:
      password = args.password
   else:
      password = getpass.getpass(prompt='Enter password for host %s and '
                                        'user %s: ' % (args.host,args.user))

   si = SmartConnect(host=args.host,
                     user=args.user,
                     pwd=password,
                     port=int(args.port))
   if not si:
       print("Could not connect to the specified host using specified "
             "username and password")
       return -1

   atexit.register(Disconnect, si)

   content = si.RetrieveContent()

   # Method 1

   for child in content.rootFolder.childEntity:
      if hasattr(child, 'vmFolder'):
         datacenter = child
         vmFolder = datacenter.vmFolder
         vmList = vmFolder.childEntity
         for vm in vmList:
            PrintVmInfo(vm)
      
      if hasattr(child, 'hostFolder'):
         datacenter = child
         hostFolder = datacenter.hostFolder
         hostList = hostFolder.childEntity
         for host in hostList:
            PrintHostInfo(host)

   # Method 2

   container = content.viewManager.CreateContainerView(
           content.rootFolder, [vim.HostSystem], True)
   for host in container.view:
      print host.name
      print host.summary.config
      #print host.summary.host.config

   container = content.viewManager.CreateContainerView(
           content.rootFolder, [vim.VirtualMachine], True)
   for vm in container.view:
       print vm.name
       print vm.summary.config

   return 0

# Start program
if __name__ == "__main__":
   main()
