# AWS Instance Port Scanner

This utility will scan the ports on your AWS instances and report which ports
are open to the public.

## Installation

Python 3 is required

You will need to ensure you have setup the standard ~/.aws/credentials and
~/.aws/config per the instructions
[here](https://docs.aws.amazon.com/amazonswf/latest/awsrbflowguide/set-up-creds.html). 

You will also need to install the boto3 python module.  This module is
included in many distribution repositories or can be installed using pip:

```sh
    $ sudo pip3 install boto3
```    

## Usage 

```
usage: aws_scanner.py [-h] [-r [REGION_PREFIXES [REGION_PREFIXES ...]]]
                      [-s START_PORT] [-e END_PORT] [-j JOBS] [-t TIMEOUT]

Scan AWS instances for open ports

optional arguments:
  -h, --help            show this help message and exit
  -r [REGION_PREFIXES [REGION_PREFIXES ...]], --region-prefixes [REGION_PREFIXES [REGION_PREFIXES ...]]
                        A list of region prefixes to limit the search to
  -s START_PORT, --start-port START_PORT
                        Starting port to scan (default: 0)
  -e END_PORT, --end-port END_PORT
                        Ending port to scan (default: 1023)
  -j JOBS, --jobs JOBS  Number of concurrent port scanning jobs (default: 1)
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout in seconds waiting for port to answer
                        (default: 5)
```

## Example

```sh
    $ ./aws_scanner.py --region-prefix=us --start-port=80 --end-port=80
    --jobs=1 --timeout=5
```  
