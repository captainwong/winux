import connection
import os
import file_op as FO
import winux_protocol

class Handler:
#     _CMD_USAGE      = 'USAGE' 
#     _CMD_HELLO      = 'HELLO'
#     _CMD_PWD        = 'PWD'
#     _CMD_LL         = 'LL'
#     _CMD_PUSH       = 'PUSH'
#     _CMD_PULL       = 'PULL'
#     _CMD_BK         = 'BACKUP'
#     _CMD_REBASE     = 'REBASE'
#     _CMD_TARGETS    = 'TARGETS'
#     _CMD_STATUS     = 'STATUS'
#     _CMD_BYE        = 'BYE'
    
    _OPTION_ALL      = '-a'
    _OPTION_FORCE    = '-f'
    _OPTION_LIST     = '-l'
    _OPTION_REMOTE   = '-r'
    
    _commands = {}
    _options = {}
    
    _client_mode = True
    _connection = None
    
    def set_client_mode(self, mode):
        self._client_mode = mode
        if self._client_mode:
            self._connection = connection.Client()
        else:
            self._connection = connection.Server()
    
    def __init__(self):
        #print 'Handler __init__'
        self._commands = {self._usage.__name__[1:] : self._usage, 
                          self._hello.__name__[1:] : self._hello, 
                          self._bye.__name__[1:] : self._bye,
                          self._ll.__name__[1:] : self._ll,
                          self._dir.__name__[1:] : self._dir,
                          self._quit.__name__[1:] : self._quit,
                          self._cd.__name__[1:] : self._cd,
                          }
        
        self._options = {self._OPTION_ALL : 'Execute command for all files.', 
                         self._OPTION_FORCE : 'Execute command forcibly.', 
                         self._OPTION_LIST : 'Show list.', 
                         self._OPTION_REMOTE : 'Remote execute this command.'}
        
        import collections
        self._commands = collections.OrderedDict(sorted(self._commands.items()))
        self._options = collections.OrderedDict(sorted(self._options.items()))
        #print self._commands
        #for key in self._commands.keys():
        #    print 'key:', key
        #    print 'value', self._commands[key].__name__
        
    def _no_connection(self):
        if self._connection.is_connected():
            return False
        else:
            print 'Connection not establihsed yet, please try command "hello [addr] [port]" to make a connection with Winux-Server.'
            return True
        
    def _recv_and_print(self):
        data = self._connection.recv()
        if data is not None:
            (ok, length, packet_type, real_data, option) = winux_protocol.ParsePacket(data)
            if ok:
                print 'Winux-Server says: ', real_data, option if option is not None else ""
            
    def handle_cmd(self, cmd, *args):
        try:
            cmd = '_' + cmd.lower()
            #print 'cmd is ', cmd
            command = getattr(self, cmd)
            #print 'command is ', command
            if callable(command):
                ret = command(cmd, *args)
                if ret is False:
                    return False
        except AttributeError as e:
            print e
            print 'Sorry, no command names "%s" or something wrong happened on calling "%s".' % (cmd[1:], cmd[1:])
        return True
    
    def _usage(self, *args):
        print 'usage: COMMAND [-OPTION]'
        print 'Commands are:'
        for key in self._commands:
            if cmp(key, self._usage.__name__[1:]) != 0:
                print '\t%s\t\t%s' % (self._commands[key].__name__[1:], self._commands[key].__doc__.strip())
        print 'Options are:'
        for key in self._options:
            print '\t%s\t\t%s' % (key, self._options[key])
        #print '\n'
        
    def _hello(self, *args):
        """
        Create a connection to Winux-Server with addr and port. e.g. "hello 8.8.8.8 10021"
        """
        if self._connection.is_connected():
            print 'Already connected with Winux-Server, please try command "bye" to disconnect.'
            return
        #print 'hello args', args, 'len', len(args)

        try:
            addr = args[1][0]
            port = int(args[1][1])
            self._connection.connect(addr, port)
            packet = winux_protocol.PackMsg('Hello!');
            self._connection.send(packet)
            self._recv_and_print()
        except (IndexError, TypeError, ValueError) as e:
            print e
            print 'Please give me a valid (addr, port).'
        else:
            print 'Now you can pull/push files via Winux-Client! Enjoy it!'
        #print 'args', args
        #print 'len', len(args)

    def _bye(self, *args):
        """
        Disconnect with Winux-Server and stop this program.
        """
        #print 'bye args', args, 'len', len(args)
        if not self._connection.is_connected():
            return False
        self._connection.disconnect()
        return False
    
    def _quit(self, *args):
        """
        Same as "bye".
        """
        return self._bye()

    def _pwd(self, *args):
        """
        Show current directory.
        """
        #print 'pwd args', args, 'len', len(args)
        if len(args) == 0 or len(args[1]) == 0:  # no option
            cur_dir = os.getcwd()
            print 'Current directory is ', cur_dir
        elif len(args[1]) == 1 and cmp(args[1][0], self._OPTION_REMOTE) == 0: # -r
            packet = winux_protocol.PackCmd('pwd')
            self._connection.send(packet)
            self._recv_and_print()
        else:
            print 'Command "pwd" has not other options except "-r".'

    def _dir(self, *args):
        """
        List directory contents.
        """
        print '_dir: args', args, 'len', len(args)
        if len(args) == 0 or len(args[1]) == 0:  # no option
            tree = FO.init_file_tree(os.getcwd())
            if len(tree.sub_folders) > 0:
                print 'Folders:'
            for f in tree.sub_folders:
                print f
            if len(tree.files) > 0:
                print 'Files:'
                print 'Name\t\t\tSize\tModified Time'
            for f in tree.files:
                fsize = f.size
                if fsize > 1024:
                    fsize /= 1024
                    print '%s\t\t%-dKB\t%s' % (f.name, fsize, f.mtime)
                else:
                    print '%s\t\t%-dB\t%s' % (f.name, fsize, f.mtime)
            del tree
        elif len(args[1]) == 1 and cmp(args[1][0], self._OPTION_REMOTE) == 0: # -r
            packet = winux_protocol.PackCmd('dir')
            self._connection.send(packet)
            self._recv_and_print()
        else:
            print 'Invalid options.'
            
    def _ll(self, *args):
        """
        Same as "pwd".
        """
        return self._dir(*args)
        
    def _cd(self, *args):
        """
        Chanage the current directory to dir.
        """
        if len(args[1]) == 1:
            dst = args[1][0]
            #print 'dst', dst
            base = os.getcwd()
            
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
                if os.path.isdir(dst):
                    os.chdir(dst)
                else:
                    print '"%s" is not a valid directory.' % dst
            self._pwd()
        elif len(args[1]) == 2:
            (op1, op2) = args[1]
            op = ''
            dst = ''
            if op1.startswith('-'):
                op = op1
                dst = op2
            elif op2.startswith('-'):
                op = op2
                dst = op1
            if cmp(op, self._OPTION_REMOTE) == 0: # -r
                packet = winux_protocol.PackCmd('cd ', dst)
                self._connection.send(packet)
                self._recv_and_print()
            else:print 'Invalid option "%s".' % op
        else:
            print 'Invalid options.'
            
        
        
        
        
        