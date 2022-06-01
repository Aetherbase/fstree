from .filetype import FileType
from .fs_tree_node import FsTreeNode
import os
class File(FsTreeNode):
    def __init__(self, filename : str, parent_dir , dry=False, content = None):
        super(File,self).__init__(filename,parent_dir)
        self.dry=dry
        if dry==False:
            if (isinstance(content,type(None))):
                self.readFs()
            elif (isinstance(content,str)):
                self.content=content
            elif(isinstance(content,bytes)):
                self.content=content
            else:
                raise Exception("Invalid content")
        else:
            self.content = None

    @staticmethod
    def from_path(path,content = None,dry=False):
        _file = FsTreeNode.from_path(path,type_hint=File,content=content,dry=dry)
        if not isinstance(_file,File):
            raise Exception(f"Invalid file path {path}")
        return _file
    
    def readFs(self,dry=None) -> None:
        __readmode : dict[FileType,tuple] = {
            FileType.TEXT : ("r",str),
            FileType.BINARY : ("rb",bytes),
            FileType.NONE : ("",type(None))
        }
        if isinstance(dry,bool):
            self.dry=dry
        if (self.in_fs==True) and (self.dry==False):
            _type=FileType.check(self.path)
            if isinstance(self.content,type(None)):
                self.content=__readmode[_type][1]()
            if not isinstance(self.content,type(None)):
                try:
                    self.content=open(self.path,mode=__readmode[self.file_type][0]).read()
                except UnicodeDecodeError:
                    self.content=bytes()
                    self.readFs()
            else:
                self.content=None

    @property
    def in_fs(self):
        return(os.path.isfile(self.path))

    @property
    def file_type(self):
        __filetype_map = {
            bytes : FileType.BINARY,
            str : FileType.TEXT,
            type(None) : FileType.NONE
        }
        return __filetype_map[type(self.content)] 

    @property
    def ext(self):
        _ext : str = os.path.splitext(self.name)[1]
        if len(_ext)>1:
            _ext=_ext[1:]
        return _ext

    def copyTo(self, dir,name=None, update_fs=False):
        if isinstance(name,type(None)):
            name=self.name
        cp_f = File(name,dir,content=self.content,dry=self.dry)
        if update_fs==True:
            cp_f.updateFs()
        return cp_f

    def updateFs(self):
        __writemode = {
            FileType.TEXT : "w",
            FileType.BINARY : "wb",
            FileType.NONE : ""
        }
        self.parent_dir.updateFs()
        if self.dry==False and not(isinstance(self.content,type(None))):
            with open(self.path,mode=__writemode[self.file_type]) as _fstream:
                _fstream.write(self.content)
                _fstream.close()

    def deleteFs(self):
        if self.in_fs:
            os.remove(self.path)
