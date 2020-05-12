#!/usr/bin/python3

# aws_scanner.py 
# Author: David Bennett - dbadapt@gmail.com
#
# Scans all regions and all instances
# and reports open ports for each instance
#
# Preqreuisites: 
#
# - Install boto3 - official Python AWS API module
# - Setup ~/.aws/credentials and ~/.aws/config (see boto3 doc)

import sys
import argparse
import boto3
from spinner import Spinner
from scanner import PortScanner

# globals
region_headers = []
zone_headers = []
spinner = Spinner() 

# process command line arguments
parser = argparse.ArgumentParser(description='Scan AWS instances for open ports')
parser.add_argument('-r','--region-prefixes', nargs='*', type=str,
        help='A list of region prefixes to limit the search to')
parser.add_argument('-s','--start-port', nargs=1, default=[0], type=int,
        help='Starting port to scan (default: %(default)s)')
parser.add_argument('-e','--end-port', nargs=1, default=[1023], type=int,
        help='Ending port to scan (default: %(default)s)')
parser.add_argument('-j','--jobs', nargs=1, default=[1], type=int,
        help='Number of concurrent port scanning jobs (default: %(default)s)')
parser.add_argument('-t','--timeout', nargs=1, default=[5], type=int,
        help='Timeout in seconds waiting for port to answer (default: %(default)s)')

args = parser.parse_args()

# display specific tag value from tag array
#
def tag_value(tag_array, key):
    """ 
    Return an AWS tag value   
  
    Parameters: 
    tag_array (array): Array of AWS tags
  
    Returns: 
    string: Tag value
 
    """
    for tag in tag_array:
        if tag['Key'] == key:
            return tag['Value']


def process_regions(region_list):
    """ 
    Process AWS regions 
  
    This function will process the AWS regions
  
    Parameters: 
    region_list (array): Region list described by boto3 
				EC2 client.describe_regions()
    """    

    for region in region_list['Regions']:

        spinner.update()

        region_name = region['RegionName']

        if not args.region_prefixes == None:
            good_region = False
            for region_prefix in args.region_prefixes[0].split(','):
                if region_name.startswith(region_prefix.lower()):
                    good_region = True
                    break
            if not good_region:
                continue

        region_client = boto3.client('ec2', region_name=region_name)

        process_zones(region_name, boto3.resource('ec2', region_name=region_name), region_client.describe_availability_zones())


def process_zones(region_name, region_resource, zone_list):
    """ 
    Process availability zones for an AWS region 
  
    Parameters: 
    region_name (str): The AWS region name (ex. us-west-1)
    region_resource (obj): The boto3 region resource
    zone_list (array): zone_list returned by boto3 describe_availability_zones()
    
    """

    for zone in zone_list['AvailabilityZones']:

        spinner.update()

        process_instances(region_name, zone['ZoneName'], region_resource.instances.all())


def process_instances(region_name, zone_name, instances):
    """ 
    Process instances within an AWS region and availability zone
  
    Parameters: 
    region_name (str): The AWS region name (ex. us-west-1)
    zone_name (str): The AWS availability zone name
    instances (array): An array of instances within the availability zone
  
    """
    for instance in instances: 

        if (zone_name == instance.placement['AvailabilityZone']):

            spinner.clear()

            if region_name not in region_headers:
                print("Region: "+region_name)
                region_headers.append(region_name)

            if zone_name not in zone_headers:
                print("\tZone: "+zone_name)
                zone_headers.append(zone_name)

            print("\t\t" + instance.id + "\t" + tag_value(instance.tags,'Name'))
            print("\t\tIP Address:" + instance.public_ip_address);

            scan_instance(instance)


def scan_instance(instance):            
    """ 
    Port scan instance and report ports
  
    This function will portscan the specified instance given the parameters
    on the command line.  See the PortScanner class in scanner.py for more info
  
    Parameters: 
    instance (obj): instance object returned by boto3
  
    Returns: 
    int: Description of return value region resource
  
    """
    scanner = PortScanner()
    scanner.target = instance.public_ip_address
    scanner.start_port = args.start_port[0]
    scanner.end_port = args.end_port[0]
    scanner.threads = args.jobs[0]
    scanner.timeout = args.timeout[0]
    ports = scanner.scan()

    if len(ports) > 0:
        for port in ports:
            print("\t\t\tPort: "+str(port['Port'])+"\t"+"Service: "+port['Service'])
    else:
        print("\t\t\tNo open ports detected")


def main():
    """ 
    This is the main function

    """

    print("""
AWS instance port scan by Region and Availability Zone
------------------------------------------------------
""")

    ec2_client = boto3.client('ec2')

    process_regions(ec2_client.describe_regions());

    spinner.clear()
    return(0)


# kick off the main function trapping keyboard cancelation
# to avoid printed stacktrace to screen
#
try:
    ret=main()
    sys.exit(ret)
except KeyboardInterrupt:
    sys.exit(1) # or 1, or whatever

