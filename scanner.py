# python class: PortScanner
# Author: David Bennett - dbadapt@gmail.com
#
# Usage:
#
# portscanner = PortScanner()
# portscanner.target = '127.0.0.1'
# portscanner.start_port = 0
# portscanner.end_port = 1024
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

class PortScanner(object):

    target = "127.0.0.1" 
    start_port = 0
    end_port = 1024
    result = []
    threads = 1
    timeout = 5
    terminate = False
    __tq = None

    __array_mutex = threading.Lock()

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

    def __make_thread(s):
        while not s.terminate:
            port=s.__tq.get()
            if port >= 0:
                s.__scan_port(port)
            s.__tq.task_done()

            
    def scan(s):
        s.result=[]
        s.__tq = Queue()
        threads = []
        for i in range(s.threads):
            thread = threading.Thread(target=s.__make_thread)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        for port in range(s.start_port, s.end_port+1):
            s.__tq.put(port)
        s.__tq.join()
        # terminate threads
        s.terminate = True
        for i in range(s.threads):
            s.__tq.put(-1)
        s.__tq.join()
        for t in threads:
            t.join()
        return(s.result)

