import os, time
from stat import ST_SIZE, ST_CTIME, ST_MTIME

_FT_FOLDER  = 0
_FT_FILE    = 1

class FileInfo:
    path    = ''
    name    = ''
    
    size = 0
    ctime = 0
    mtime = 0
    
class FileTree:
    def __init__(self):
        self.path = ''
        
        self.files = []
        self.sub_folders = []
    
    
def init_file_tree(base_path):
    #curdir = os.getcwd()
    print 'Scanning folder: ' + base_path
    tree = FileTree()
    tree.path = base_path
    for root, dirs, files in os.walk(base_path):
        for cur_file in files:
            file_info = FileInfo()
            file_info.name = cur_file
            file_info.path = os.path.join(root, cur_file)
            st = os.stat(file_info.path)
            file_info.size = st[ST_SIZE]
            file_info.ctime = time.asctime(time.localtime(st[ST_CTIME]))
            file_info.mtime = time.asctime(time.localtime(st[ST_MTIME]))
            tree.files.append(file_info)
        for d in dirs:
            tree.sub_folders.append(d)
        
        tree.files.sort()
        tree.sub_folders.sort()
        break
    return tree       
            
            
            
            
            
            