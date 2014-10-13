from crc16_ibm import crc16_ibm as crc16

TYPE_MSG = 'msg'
TYPE_CMD = 'cmd'

def PackMsg(msg):
    packet_type = 'packet_type = %s\r\n' % TYPE_MSG
    length = 'length = %d\r\n' % len(msg)
    crcsum = 'crc = %04x\r\n' % crc16.crc16_ibm(msg)
    packet = packet_type + length + crcsum + msg
    return packet

#def PackMsg(msg):
#    return _PackPacket(TYPE_MSG, msg)

def PackCmd(cmd, option = None):
    #return _PackPacket(TYPE_CMD, cmd, option)
    packet_type = 'packet_type = %s\r\n' % TYPE_CMD
    cmd = 'command = %s\r\n' % cmd
    option = 'option = %s\r\n' % (option if option is not None else 'None',)
    data = cmd + option
    length = 'length = %d\r\n' % len(data)
    crcsum = 'crc = %04x\r\n' % crc16.crc16_ibm(data)
    packet = packet_type + length + crcsum + data
    return packet

def ParsePacket(data):
    data_len = len(data)
    lines = data.split('\r\n')
    if lines[0].startswith('packet_type = ') and lines[1].startswith('length = ') and lines[2].startswith('crc = '):
        packet_type = lines[0][len('packet_type = '):].strip()
        length = int(lines[1][len('length = '):].strip())
        crcsum = lines[2][len('crc = '):].strip()
        
        local_length = len(lines[0]) + len(lines[1]) + len(lines[2]) + 6 + int(length)
        real_data = data[(local_length - length):]
        local_crcsum = '%04x' % crc16.crc16_ibm(real_data)
        
        if local_length <= data_len and cmp(crcsum, local_crcsum) == 0:
            if cmp(packet_type, TYPE_MSG) == 0:
                return (True, local_length, packet_type, real_data, None)
            elif cmp(packet_type, TYPE_CMD) == 0:
                if lines[3].startswith('command = ') and lines[4].startswith('option = '):
                    real_data = lines[3][len('command = '):].strip()
                    option = lines[4][len('option = '):].strip()
                    return (True, local_length, packet_type, real_data, option)
                else:
                    return (False, 0, 0, 0, 0)
            else:
                return (False, 0, 0, 0, 0)
    return (False, 0, 0, 0, 0)





