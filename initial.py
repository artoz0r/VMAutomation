"""Just a skellington to help me get started"""

import atexit
import argparse
import getpass

from pyVim import connect
from pyVmomi import vmodl

## Couldn't figure out how to connect to vCenter in my case so I am using "hello_world_vcenter.py" as baseline

def get_args(): ## Using this as a temporary solution while thinking about how I can hide variables in the best possible way
    """Get command line args from the user.
    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter')

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

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args

def main():

    args = get_args()
    try:
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port))

        atexit.register(connect.Disconnect, service_instance)

# Start program
if __name__ == "__main__":
    main()


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