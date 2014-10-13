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
        (ok, length, packet_type, real_data, option) = winux_protocol.ParsePacket(data)
        if ok:
            if (option is None) or (cmp(option, 'None') == 0):
                print 'Client says:', real_data
            else:
                print 'Client says:', real_data, option
            
            if cmp(packet_type, winux_protocol.TYPE_MSG) == 0:
                pass
            elif cmp(packet_type, winux_protocol.TYPE_CMD) == 0:
                self.handle_cmd(real_data, option)
            else:
                print 'Invalid packet type:', packet_type
            if len(data) - length > 0:
                self.dataReceived(data[length:])
        else:
            print 'Error data:\n', data
                
    def handle_cmd(self, cmd, option = None):
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
        
class WinuxServerFactory(protocol.Factory):
    numConnections = 0
    def buildProtocol(self, addr):
        return WinuxServer(self)
        
if __name__=='__main__':
    
    reactor.listenTCP(10021, WinuxServerFactory())#@UndefinedVariable
    print 'server started...'
    reactor.run()#@UndefinedVariable


