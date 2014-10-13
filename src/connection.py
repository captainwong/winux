import socket
import winux_protocol as wp
import file_op as FO
import time

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
    
    def send_files(self, files, option = None):
        if self._connection_established:
            for fpath in files:
                self._send_file(fpath, option)
    
    def _send_file(self, fpath, option = None):
        fname = FO.get_file_name_from_full_path(fpath)
        self._socket.sendall(wp.PackFileHead(fname, option))
        fs = open(fpath, 'rb')
        fdata = fs.read(1024)
        while fdata:
            time.sleep(0.1)
            if len(fdata) < 1024:
                self._socket.sendall(wp.PackFileData(fdata, True))
            else:
                self._socket.sendall(wp.PackFileData(fdata))
            fdata = fs.read(1024)
        fs.close()
        
class Server(_Connection):
    def __init__(self):
        _Connection.__init__(self)
        
        
        