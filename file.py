from .filetype import FileType
from .fs_tree_node import FsTreeNode
import os
class File(FsTreeNode):
    def __init__(self, filename : str, parent_dir , dry=True, content = None):
        super(File,self).__init__(filename,parent_dir)
        self.dry=dry
        if dry==False:
            if (type(content)==type(None)) :
                self.readFs()
            elif (type(content)==str):
                self.content=content
                self.type=FileType.TEXT
            elif(type(content)==bytes):
                self.content=content
                self.type=FileType.BINARY
            else:
                raise Exception("Invalid content")
        else:
            self.content = None

    @staticmethod
    def from_path(path,content = None,dry=True):
        return FsTreeNode.from_path(path,type_hint=File,content=content,dry=dry)
    
    def readFs(self,dry=None):
        __readmode = {
            FileType.TEXT : "r",
            FileType.BINARY : "rb"
        }
        if type(dry)==bool:
            self.dry=dry
        if (self.in_fs==True) and (self.dry==False):
            self.type=FileType.check(self.path)
            try:
                self.content=open(self.path,mode=__readmode[self.type]).read()
            except UnicodeDecodeError:
                self.type=FileType.BINARY
                self.readFs()
        else:
            if hasattr(self,"type"):
                del self.type
            self.content=None


    @property
    def in_fs(self):
        return(os.path.isfile(self.path))
    
    @property
    def ext(self):
        _ext = os.path.splitext(self.name)[1]
        if len(_ext)>1:
            _ext=_ext[1:]
        return _ext

    def copyTo(self, dir,name=None, update_fs=False):
        if type(name)==type(None):
            name=self.name
        cp_f = File(name,dir,content=self.content,dry=self.dry)
        if update_fs==True:
            cp_f.updateFs()
        return cp_f

    def updateFs(self):
        __writemode = {
            FileType.TEXT : "w",
            FileType.BINARY : "wb"
        }
        self.parent_dir.updateFs()
        if self.dry==False:
            with open(self.path,mode=__writemode[self.type]) as _fstream:
                _fstream.write(self.content)
                _fstream.close()

    def deleteFs(self):
        if self.in_fs:
            os.remove(self.path)
