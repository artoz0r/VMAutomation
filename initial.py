# 
# Written by Artem Chatlikov
# https://github.com/artoz0r/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import atexit
import argparse
import getpass
import hashlib

import requests

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

## Couldn't figure out how to connect to vCenter in my case so I am using "hello_world_vcenter.py" as baseline

def get_args(): # Get arguments: In test environment from console with flags, later on frontend will handle this
    """Get command line args from the user."""

    parser = argparse.ArgumentParser(
        description='Arguments for running the program')

    # because -h is reserved for 'help' we use -s for service
    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    # because we want -p for password, we use -o for port
    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    # username to vCenter
    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    # password for vCenter user
    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    # flag to signal program to create a virtual machine with user parameters
    parser.add_argument('-c', '--createvm',
                        required=False,
                        action='store',
                        help='Argument to create virtual machine')

    # flag to signal program to start a virtual machine
    parser.add_argument('-k', '--startvm',
                        required=False,
                        action='store',
                        help='Argument to start a virtual machine')

    # flag to signal program to shut down a virtual machine
    parser.add_argument('-d', '--shutdownvm',
                        required=False,
                        action='store',
                        help='Argument to shut down a virtual machine')

    # flag to signal program to delete a virtual machine
    parser.add_argument('-e', '--deletevm',
                        required=False,
                        action='store',
                        help='Argument to delete a virtual machine')

    # get virtual machine name for multiple purposes (adding disk, nic...)
    parser.add_argument('-n', '--vm-name',
                        required=True,
                        action='store',
                        help='Name of the virtual machine we want to work on')

    # Define VM disk type, thin or thick provisioned (new vm)
    parser.add_argument('--disk-type',
                        required=False,
                        action='store',
                        default='thin',
                        choices=['thick', 'thin'],
                        help='thick or thin')

    # Define disk size (new vm)
    parser.add_argument('--disk-size',
                        required=True,
                        action='store',
                        help='disk size, in GB, to add to the VM')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args

args = get_args()

service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port))

atexit.register(connect.Disconnect, service_instance)

content = service_instance.RetrieveContent()
datacenter = content.rootFolder.childEntity[0]
vm_folder = datacenter.vmFolder
hosts = datacenter.hostFolder.childEntity
resource_pool = hosts[0].resourcePool

def get_obj(content, vimtype, name): ## Used for retrieving objects from vCenter
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

vm = get_obj(content, [vim.VirtualMachine], args.vm_name)

def vmcreate(): ## Incoming request from api with user defined parameters and creating a virtual machine in vCenter
    datastore_path = '[ESXI2] vm1'

    vmx_file = vim.vm.FileInfo(logDirectory=None,
                               snapshotDirectory=None,
                               suspendDirectory=None,
                               vmPathName=datastore_path)

    config = vim.vm.ConfigSpec(
                                name=args.vm_name,
                                memoryMB=1024,
                                numCPUs=1,
                                files=vmx_file,
                                guestId=None,
                                version='vmx-08'
                              )

    task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)

    print "--- Creating a new virtual machine ---"

    vm = None

    if vm == get_obj(content, [vim.VirtualMachine], args.vm_name):
    	print "Looking for vm"
        add_disk(vm, service_instance, args.disk_size, args.disk_type)
    else:
        print "--- VM not found ---"

def add_disk(vm, service_instance, disk_size, disk_type):
        spec = vim.vm.ConfigSpec()
        # get all disks on a VM, set unit_number to the next available
        for dev in vm.config.hardware.device:
            if hasattr(dev.backing, 'fileName'):
                unit_number = int(dev.unitNumber) + 1
                # unit_number 7 reserved for scsi controller
                if unit_number == 7:
                    unit_number += 1
                if unit_number >= 16:
                    print "Maximum of 15 disks supported for each VM"
                    return
            if isinstance(dev, vim.vm.device.VirtualSCSIController):
                controller = dev
        # add disk here
        dev_changes = []
        new_disk_kb = int(disk_size) * 1024 * 1024
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.fileOperation = "create"
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        disk_spec.device = vim.vm.device.VirtualDisk()
        disk_spec.device.backing = \
            vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        if disk_type == 'thin':
            disk_spec.device.backing.thinProvisioned = True
        disk_spec.device.backing.diskMode = 'persistent'
        disk_spec.device.unitNumber = unit_number
        disk_spec.device.capacityInKB = new_disk_kb
        disk_spec.device.controllerKey = controller.key
        dev_changes.append(disk_spec)
        spec.deviceChange = dev_changes
        vm.ReconfigVM_Task(spec=spec)
        print "%sGB disk added to %s" % (disk_size, vm.config.name)

def vmstart(): ## Starting a virtual machine in vCenter
    pass

def vmshutdown(): ## Shutting down a virtual machine in vCenter
    pass

def vmdelete(): ## Deleting a virtual machine from disk in vCenter
    pass

def main():

    if args.createvm == 'yes':
        vmcreate()
    elif args.startvm == 'yes':
        vmstart()
    elif args.shutdownvm == 'yes':
        vmshutdown()
    elif args.deletevm == 'yes':
        vmdelete()
    elif disk_size > 0:
        add_disk(vm, service_instance, args.disk_size, args.disk_type)

# Start program
if __name__ == "__main__":
    main()