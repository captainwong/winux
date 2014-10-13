from crc16_ibm import crc16_ibm as crc16

# TYPE_MSG = 'msg'
# TYPE_CMD = 'cmd'
# TYPE_FILE_HEAD = 'file_head'
# TYPE_FILE_DATA = 'file_data'
# TYPE_FILE_END  = 'file_end'

def PackMsg(msg):
    cmd = 'command = msg\r\n'
    option = 'option = none\r\n'
    length = 'length = %d\r\n' % len(msg)
    crcsum = 'crc = %04x\r\n' % crc16.crc16_ibm(msg)
    packet = cmd + option + length + crcsum + msg
    return packet

#def PackMsg(msg):
#    return _PackPacket(TYPE_MSG, msg)

def PackCmd(cmd, option = None):
    cmd = 'command = %s\r\n' % cmd
    option = 'option = %s\r\n' % (option if option is not None else 'None',)
    length = 'length = 0\r\n'
    crcsum = 'crc = 0000\r\n'
    packet = cmd + option + length + crcsum
    return packet

def PackFileHead(fname, option = None):
    cmd = 'command = file_head\r\n'
    option = 'option = %s\r\n' % (option if option is not None else 'None',)
    body = fname
    length = 'length = %d\r\n' % len(body)
    crcsum = 'crc = %04x\r\n' % crc16.crc16_ibm(body)
    packet = cmd + option + length + crcsum + body
    return packet

def PackFileData(fdata, tail = False):
    cmd = 'command = %s\r\n' % ('file_data' if not tail else 'file_tail',)
    option = 'option = None\r\n'
    body = fdata
    length = 'length = %d\r\n' % len(body)
    crcsum = 'crc = %04x\r\n' % crc16.crc16_ibm(body)
    packet = cmd + option + length + crcsum + body
    return packet


def ParsePacket(data):
    data_len = len(data)
    lines = data.split('\r\n')
    if len(lines) >= 5:
        while True:
            if not lines[0].startswith('command = '):
                break
            if not lines[1].startswith('option = '):
                break
            if not lines[2].startswith('length = '):  
                break
            if not lines[3].startswith('crc = '):
                break
            
            command = lines[0][len('command = '):].strip()
            option = lines[1][len('option = '):].strip()    
            body_length = int(lines[2][len('length = '):].strip())
            body_crcsum = lines[3][len('crc = '):].strip()
            
            bytes_commited = len(lines[0]) + len(lines[1]) + len(lines[2]) + len(lines[3]) + 8 + int(body_length)
            body = data[(bytes_commited - body_length):]
            
            if bytes_commited > data_len:
                break
            
            if len(body) != 0 or cmp(body_crcsum, '0000') != 0:
                local_crcsum = '%04x' % crc16.crc16_ibm(body)
                if cmp(body_crcsum, local_crcsum) != 0:
                    break
            
            return (True, bytes_commited, command, option, body)

    return (False, 0, 0, 0, 0)





