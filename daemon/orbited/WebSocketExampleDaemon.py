from socket import *
import threading

class Handler(threading.Thread):
    def __init__(self, sock, addr):
        threading.Thread.__init__(self)
        self.sock = sock
        self.addr = addr
        
    def run(self):
       buffer = ""
       state = "initial"
       while True:
            data = self.sock.recv(1024)
            if not data: break
            buffer += data
            if state == "initial":
                i = buffer.find('\r\n\r\n')
                if i == -1:
                    continue
                response, extra = buffer.split('\r\n\r\n', 1)
                status, headers = response.split('\r\n', 1)
                headers = dict([ d.split(': ') for d in headers.split('\r\n') ])
                error = False
                if not status.startswith('OPTIONS '):
                    print 'invalid method'
                    error = True
                elif headers.get('Upgrade', None) != 'WebSocket/1.0':
                    print 'invalid (or missing) Upgrade header'
                    error = True
                if error:
                    self.sock.send('HTTP/1.1 400 Invalid Protocol\r\n\r\n')
                    break
                self.sock.send('HTTP/1.1 101 Switching Protocols\r\nUpgrade: WebSocket/1.0\r\n\r\n')
                buffer = buffer[i+1:]
                state = "echo"
            if state == "echo":
                while True:
                    i = buffer.find('\x00')
                    if i == -1:
                        break
                    j = buffer.find('\x00', i+1)
                    if j == -1:
                        break
                    payload = buffer[i+1:j]
                    self.sock.send('\x00ECHO: ' + payload + '\x00')
                    buffer = buffer[j+1:]
                    
       self.sock.close()
       
if __name__=='__main__':
       serversock = socket(AF_INET, SOCK_STREAM)
       serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
       serversock.bind(('', 9998))
       serversock.listen(2)
       while True:
             print 'waiting for connections'
             clientsock, addr = serversock.accept()
             print 'connected from:', addr
             h = Handler(clientsock, addr)
             h.start()


