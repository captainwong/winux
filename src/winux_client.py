import cmd_handler


def parse_cmd():
    content = raw_input('Enter a command:')
    #print content
    t = tuple(content.split())
    #print t
    cmd = t[0]
    args = t[1:]
    return (cmd, args)

if __name__ == '__main__':
    print 'Welcom to use Winux-Client! Type a command to get start!'
    handler = cmd_handler.Handler()
    handler.set_client_mode(True)
    handler.handle_cmd('usage')
    #handler.handle_cmd('hello', '192.168.0.221', 10021)
    while True:
        #(cmd, args) = parse_cmd()
        #try:
        content = raw_input('Enter a command:')
        t = tuple(content.split())
        #print 't', t
        cmd = t[0]
        args = t[1:]
        #print 'args', args
        if handler.handle_cmd(cmd, args) is False:
            break
        #except:
        #    break
            
    print '\nGoodbye!'
    
    
    
    
    
    
    
    