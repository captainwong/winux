import socket

_MODE_CLIENT = 0
_MODE_SERVER = 1

class _Connection:
    _mode = _MODE_CLIENT
    _socket = None
    _connection_established = False
    _sock_addr = None
    
    def __init__(self):
        pass
    
class Client(_Connection):
    def __init__(self):
        _Connection.__init__(self)
        
    def is_connected(self):
        return self._connection_established
    
    def connect(self, serv_addr, serv_port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect((serv_addr, serv_port))
        except socket.error as e:
            print e
        else:
            print 'Connection with winux_server ok,', self._socket.getpeername()
            self._connection_established = True
        return self._connection_established
    
    def disconnect(self):
        if self._connection_established:
            self._socket.close()
            self._connection_established = False
            print 'Disconnected.'
    
    def send(self, content):
        if self._connection_established:
            self._socket.send(content)
    
    def recv(self):
        if self._connection_established:
            data = self._socket.recv(1024)
            return data
        return None
        
class Server(_Connection):
    def __init__(self):
        _Connection.__init__(self)
        
        
        