# python class: PortScanner
# Author: David Bennett - dbadapt@gmail.com
#
# Usage:
#
# portscanner = PortScanner()
# portscanner.target = '127.0.0.1'
# portscanner.start_port = 0
# portscanner.end_port = 1023
# portscanner.timeout = 1
# portscanner.threads = 4
# port_array = portscanner.scan()
#
# Returns:
#
# port_array result from scan() method is an array
# of  {'Port':int,'Service':str}

import threading
from queue import Queue
import time
import socket
from spinner import Spinner

class PortScanner(object):
    """
    This class implements a multi-threaded port scanner in Python

    This is a simple port scanner that attempts to open a TCP connection
    on an IP address.   If the connection attempt is successful then the
    port scan is successful.


    Attributes
    ----------
    target : str
        IP address or hostname to be scanned (default is 127.0.0.1)
    start_port : int
        the start of the port range from 0-65535 to scan (default is 0)
    end_port  : int
        the end of the port range from 0-65535 to scan (default is 1023)
    threads : int
        the number of simultaneous port scanning threads to start (default is 1)
    timeout : int
        timeout in seconds when trying to open a connection on a port (default is 5)

    Methods
    -------
    scan()
        Perform the port scan
    """
    target = "127.0.0.1" 
    start_port = 0
    end_port = 1023
    result = []
    threads = 1
    timeout = 5
    __terminate = False
    __tq = None
    __spinner = Spinner()

    __array_mutex = threading.Lock()
    __spin_mutex = threading.Lock()

    def result_contains_port(s,port):
        for r in s.result:
            if r['Port'] == port:
                return True;
        return False;

    # pushes answering ports into result array
    def __scan_port(s,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(s.timeout)
        try:
            con = sock.connect((s.target, port))
            element = {'Port':port, 'Service':socket.getservbyport(port)}
            with s.__array_mutex:
                s.result.append(element)
            con.close()
        except:
            pass

    # the main thread method
    def __make_thread(s):
        while not s.__terminate:
            port=s.__tq.get()
            if port >= 0:
                s.__scan_port(port)
            s.__tq.task_done()

    # spinner thread
    def __spinner_thread(s):
        while not s.__terminate:
            with s.__spin_mutex:
                s.__spinner.update()
            time.sleep(0.2)

    # this is the public scan() method
    def scan(s):
        s.result=[]
        s.__tq = Queue()
        active_threads = []
        for i in range(s.threads):
            thread = threading.Thread(target=s.__make_thread)
            thread.daemon = True
            thread.start()
            active_threads.append(thread)
        for port in range(s.start_port, s.end_port+1):
            s.__tq.put(port)
        # spinner thread
        spinner_thread = threading.Thread(target=s.__spinner_thread)
        spinner_thread.daemon = True
        spinner_thread.start()
        active_threads.append(spinner_thread)
        # wait for all items in queue to be processed
        s.__tq.join()
        # terminate threads
        s.__terminate = True
        for i in range(s.threads):
            s.__tq.put(-1)
        s.__tq.join()
        for t in active_threads:
            t.join()
        s.__spinner.clear()
        return(s.result)

