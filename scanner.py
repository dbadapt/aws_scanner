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
    __tq = None

    __array_mutex = threading.Lock()

    # pushes answering ports into result array
    def __scan_port(s,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            con = sock.connect((s.target, port))
            with __array_mutex:
                s.result.append(port)
            con.close()
        except:
            pass

    def __make_thread(s):
        while True:
            port=s.__tq.get()
            s.__scan_port(port)
            s.__tq.task_done()
            
    def scan(s):
        s.__tq = Queue()
        for i in range(s.threads):
            thread = threading.Thread(target=s.__make_thread)
            thread.daemon = True
            thread.start()
        for port in range(s.start_port, s.end_port):
            s.__tq.put(port)
        s.__tq.join()
        return(s.result)


