import os
if os.name != 'nt':
    from twisted.internet import epollreactor
    epollreactor.install()
else:
    from twisted.internet import iocpreactor
    iocpreactor.install()
from twisted.internet import protocol, reactor
import winux_protocol
import file_op as FO
#import datetime



class WinuxServer(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.cur_file = None
        
    def connectionMade(self):
        #self.client_id = self.factory.numConnections
        self.factory.numConnections += 1
        print 'new connection from', self.transport.getPeer(), 'Total : ', self.factory.numConnections
        self.transport.write(winux_protocol.PackMsg('Hi!'));
        
    def connectionLost(self, reason):
        self.factory.numConnections -= 1
        print self.transport.getPeer(), 'disconnected', 'Total : ', self.factory.numConnections

    def dataReceived(self, data):
        #print data
        (ok, bytes_commited, command, option, body) = winux_protocol.ParsePacket(data)
        if ok:
            if cmp(command, 'msg') == 0:
                print 'Client says: %s' % (body)
            else:
                self.handle_cmd(command, option, body)

            if len(data) - bytes_commited > 0:
                self.dataReceived(data[bytes_commited:])
        else:
            print 'Error data:\n', data
                
    def handle_cmd(self, cmd, option = None, body = None):
        if cmp(cmd, 'pwd') == 0:
            cur_dir = os.getcwd()
            packet = 'Current directory is ' + cur_dir
            print packet
            packet = winux_protocol.PackMsg(packet)
            self.transport.write(packet)
        elif cmp(cmd, 'dir') == 0:
            tree = FO.init_file_tree(os.getcwd())
            packet = ''
            if len(tree.sub_folders) > 0:
                packet += 'Folders:\n'
            for f in tree.sub_folders:
                packet += f + '\n'
            if len(tree.files) > 0:
                packet += 'Files:\n'
                packet += 'Name\t\t\tSize\tModified Time\n'
            for f in tree.files:
                fsize = f.size
                if fsize > 1024:
                    fsize /= 1024
                    packet += '%s\t\t%-dKB\t%s\n' % (f.name, fsize, f.mtime)
                else:
                    packet += '%s\t\t%-dB\t%s\n' % (f.name, fsize, f.mtime)
            packet = winux_protocol.PackMsg(packet)
            self.transport.write(packet)
        elif cmp(cmd, 'cd') == 0:
            base = os.getcwd()
            dst = option# if option is not None else ''
            
            if cmp(dst, '.') == 0:
                pass
            elif cmp(dst, '..') == 0:
                l = base.split(os.sep)
                l = l[:-1]
                #print 'l', l
                dst = os.sep.join(l)
                #print 'dst', dst
                os.chdir(dst)
            elif os.path.isdir(dst):
                os.chdir(dst)
            else:
                dst = os.path.join(base, dst)
                if dst is not None and os.path.isdir(dst):
                    os.chdir(dst)
                else:
                    packet = '"%s" is not a valid directory.' % dst if dst is not None else ''
                    packet = winux_protocol.PackMsg(packet)
                    self.transport.write(packet)
            self.handle_cmd('pwd')
        elif cmp(cmd, 'file_head') == 0:
            if self.cur_file is not None and not self.cur_file.closed:
                self.cur_file.close()
            self.cur_file = open(body, 'w')
            print 'Client uploading file %s ......' % body
        elif cmp(cmd, 'file_data') == 0:
            if self.cur_file is not None and not self.cur_file.closed:
                self.cur_file.write(body)
        elif cmp(cmd, 'file_tail') == 0:
            if self.cur_file is not None and not self.cur_file.closed:
                self.cur_file.write(body)
                size = self.cur_file.tell()
                if size < 1024: size = '%dBytes' % size
                else:           size = '%dKB' % (size / 1024)
                print 'Client uploaded file %s %s' % (self.cur_file.name, size)
                self.cur_file.close()
                
class WinuxServerFactory(protocol.Factory):
    numConnections = 0
    def buildProtocol(self, addr):
        return WinuxServer(self)
        
if __name__=='__main__':
    
    reactor.listenTCP(10021, WinuxServerFactory())#@UndefinedVariable
    print 'server started...'
    reactor.run()#@UndefinedVariable


