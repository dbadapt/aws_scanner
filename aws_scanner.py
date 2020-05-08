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


def tag_value(tag_array, key):
    for tag in tag_array:
        if tag['Key'] == key:
            return tag['Value']

def main():
    parser = argparse.ArgumentParser(description='Scan AWS instances for open ports')
    parser.add_argument('--region-prefixes', nargs='*', type=str,
            help='A list of region prefixes to limit the search to')

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
                        sys.stdout.write("Region: "+region_name+"\n")
                        region_printed = True

                    if not zone_printed:
                        sys.stdout.write("\tZone: "+zone_name+"\n")
                        zone_printed = True

                    sys.stdout.write("\t\t" + instance.id + "\t" + tag_value(instance.tags,'Name')+"\n")

    spinner.clear()
    return(0)

try:
    ret=main()
    sys.exit(ret)
except KeyboardInterrupt:
    sys.exit(1) # or 1, or whatever

