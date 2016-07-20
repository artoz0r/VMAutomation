"""Just a skellington to help me get started"""

import atexit

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

args = cli.get_args()

try:
    service_instance = connect.SmartConnect(host=args.host,
                                            user=args.user,
                                            pwd=args.password,
                                            port=int(args.port))

    atexit.register(connect.Disconnect, service_instance)


def main():
	pass

def vmrequest(userid, diskrequest,processorrequest,ramrequest): ## Incoming request from api with user defined parameters
	pass

def vmcreate(): ## Creating a virtual machine in vCenter
	pass

def vmstart(): ## Starting a virtual machine in vCenter
	pass

def vmshutdown(): ## Shutting down a virtual machine in vCenter
	pass

def vmdelete(): ## Deleting a virtual machine from disk in vCenter
	pass