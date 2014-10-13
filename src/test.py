from cmd_handler import Handler
import global_val

def test_handler():    
    handler = Handler()
    handler.set_client_mode(True)
    handler.handle_cmd('usage')
    handler.handle_cmd('hello', '192.168.0.221', 10021)
    #import socket
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s = socket.create_connection(('192.168.0.221', 7891), timeout = 0)
    
def test_connection():
    from connection import Client
    client = Client()
    client.connect(global_val.SERVER_ADDR, global_val.SERVER_PORT)
    
if __name__ == "__main__":
    test_handler()
    #test_connection()
    
    
    
    
    
    
    