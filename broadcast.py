'''This program demonstrate the broadcast mechanism'''

from socket import (
    socket,
    AF_INET, 
    SOCK_STREAM
)

import threading
import time



class Connection:
    def __init__(self, transport, active=True):
        self.transport = transport
        self.active = active
    
    def __repr__(self):
        return 'Connection: %r' % self.con


class Server:

    def __init__(self, host, port):
        self._sock = socket(AF_INET, SOCK_STREAM)
        self._sock.bind((host, port))
        self._sock.listen()
        
        self._connections = set()
        self._closed_connections = set()
        self.is_running = False
        self.closed = False
        threading.Thread(target=self._broadcast_message, daemon=True).start()

    
    def _broadcast_message(self):
        while True:
            
            if not self._connections:
                time.sleep(0.1)
                continue
            #if there is some connections then 
            for con in self._connections:
                #if trasport is not closed then only call the send the message
                print(con.active)
                try:
                    con.active and con.transport.send('Here is somethifn'.encode())
                except BrokenPipeError as e:
                    con.active = False
                    con.transport.close()
                    self._closed_connections.add(con)
            
            #we finnaly clean up the connections
            #discard all the connection which are deactive

            time.sleep(2)
            self.clean_up()
            print(len(self._connections))


    def clean_up(self):
        
        if self._closed_connections:
            self._connections.difference_update(self._closed_connections)

    def run(self):
        if not self.is_running:
            self.is_running = True
        while not self.closed:
            transport, addr = self._sock.accept()
            print(transport)
            #now once the connection is made , put the trasport
            self._connections.add(Connection(transport, True))
            #and then we are done
    


        

def main():
    s = Server('localhost', 7000)
    s.run()

if __name__ == '__main__':
    main()


