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

# display specific tag value from tag array
def tag_value(tag_array, key):
    for tag in tag_array:
        if tag['Key'] == key:
            return tag['Value']

def main():

    parser = argparse.ArgumentParser(description='Scan AWS instances for open ports')
    parser.add_argument('-r','--region-prefixes', nargs='*', type=str,
            help='A list of region prefixes to limit the search to')
    parser.add_argument('-s','--start-port', nargs=1, default=0, type=int,
            help='Starting port to scan (default: %(default)s)')
    parser.add_argument('-e','--end-port', nargs=1, default=1023, type=int,
            help='Ending port to scan (default: %(default)s)')
    parser.add_argument('-j','--jobs', nargs=1, default=1, type=int,
            help='Number of concurrent port scanning jobs (default: %(default)s)')
    parser.add_argument('-t','--timeout', nargs=1, default=[5], type=int,
            help='Timeout in seconds waiting for port to answer (default: %(default)s)')

    args = parser.parse_args()

    spinner = Spinner() 

    ec2_client = boto3.client('ec2')

    region_list = ec2_client.describe_regions()

    print("""
AWS instance port scan by Region and Availability Zone
------------------------------------------------------
    """)

    for region in region_list['Regions']:

        region_name = region['RegionName']

        if not args.region_prefixes == None:
            good_region = False
            for region_prefix in args.region_prefixes[0].split(','):
                if region_name.startswith(region_prefix.lower()):
                    good_region = True
                    break
            if not good_region:
                continue

        region_printed = False

        spinner.update()

        region_client = boto3.client('ec2', region_name=region_name)

        region_resource = boto3.resource('ec2', region_name=region_name)

        zone_list = region_client.describe_availability_zones()

        for zone in zone_list['AvailabilityZones']:

            spinner.update()

            zone_printed = False
            zone_name = zone['ZoneName']
        
            for instance in region_resource.instances.all():

                if (zone_name == instance.placement['AvailabilityZone']):

                    spinner.clear()

                    if not region_printed:
                        print("Region: "+region_name)
                        region_printed = True

                    if not zone_printed:
                        print("\tZone: "+zone_name)
                        zone_printed = True

                    print("\t\t" + instance.id + "\t" + tag_value(instance.tags,'Name'))
                    print("\t\tIP Address:" + instance.public_ip_address);

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

    spinner.clear()
    return(0)

try:
    ret=main()
    sys.exit(ret)
except KeyboardInterrupt:
    sys.exit(1) # or 1, or whatever

