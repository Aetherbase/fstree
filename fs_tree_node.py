
import abc
import os

class FsTreeNode(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,name,parent_dir,allow_hidden=False):
        from .file import File
        if type(self)==FsTreeNode:
            raise Exception("Not legal to create a direct object")
        if isinstance(self,File):
            if name in ["","/",".",".."]:
                raise Exception("Illegal name for a file")
        self.name = name
        self.set_parent(parent_dir,allow_hidden=allow_hidden)
    
    @staticmethod
    def from_path(path,type_hint=None,**kwargs):
        from .directory import Directory
        from .file import File
        if (os.path.exists(path)):
            if os.path.isdir(path):
                type_hint=Directory
            elif os.path.isfile(path):
                type_hint=File

        if isinstance(type_hint,type) and issubclass(type_hint,FsTreeNode):
            basename = os.path.basename(path)
            dirname = os.path.dirname(path)
            if len(basename)==0:
                raise Exception("Empty basename is not allowed")
            if dirname=="/":
                return type_hint(basename,Directory.ROOT,**kwargs)
            elif dirname=="":
                return type_hint(basename,Directory.NULL,**kwargs)
            return type_hint(basename,dirname,**kwargs)
        else:
            raise Exception("Unable to determine node type")

    def set_parent(self,parent_dir,allow_hidden=False):
        from .directory import Directory
        if isinstance(parent_dir,str):
            parent_dir = Directory.from_path(parent_dir,dry=True,allow_hidden=allow_hidden)
        elif isinstance(parent_dir,type(None)):
            parent_dir = Directory.NULL
        if (not isinstance(parent_dir,Directory)) and  not (self.name=="" and isinstance(self,Directory)):
            raise Exception("Invalid type for parent dir")
        self.parent_dir : Directory = parent_dir
        if isinstance(self.parent_dir, Directory):
            if not self.parent_dir.is_same_path(Directory.NULL):
                if self.parent_dir.dry==False:
                    self.parent_dir.children[self.name]=self

    @property
    def path(self):
        if self.parent_dir==None:
            return self.name
        return os.path.join(self.parent_dir.path,self.name)

    def get_relative_to(self,dir,**kwargs):
        from .directory import Directory
        from .file import File
        if not isinstance(dir,Directory):
            raise Exception("invalid dir type")
        _self_ancestors=self.ancestor_list
        _remote_parent_ancestors = dir.ancestor_list
        if len(_remote_parent_ancestors)<len(_self_ancestors):
            relative_ancestors=_self_ancestors[:-len(_remote_parent_ancestors)-1]
            if len(relative_ancestors)==0:
                if isinstance(self,Directory):
                    return Directory(self.name,Directory.NULL,children=self.children,dry=self.dry,dry_files=self.dry_files,**kwargs)
                if isinstance(self,File):
                    return File(self.name,Directory.NULL,dry=self.dry,content=self.content)
            _hp=relative_ancestors.pop()
            relative_ancestors.reverse()
            if _hp.parent_dir.is_same_path(dir):
                last_parent = Directory(_hp.name,Directory.NULL,children=_hp.children,dry=_hp.dry,**kwargs)
                for _parent in relative_ancestors:
                    last_parent = Directory(_parent.name,last_parent,children=_parent.children,dry=_parent.dry,**kwargs)
                if isinstance(self,Directory):
                    return Directory(self.name,last_parent,children=self.children,dry=self.dry,dry_files=self.dry_files,**kwargs)
                if isinstance(self,File):
                    return File(self.name,last_parent,dry=self.dry,content=self.content)
            else:
                raise Exception("Invalid directory for relative calculation")
        else:
            raise Exception("the parent dir should be at higher position in hierarchy than child's")

    def is_same_path(self,fs_object):
        if isinstance(fs_object,str):
            return os.path.samefile(fs_object,self.path)
        if not isinstance(fs_object,FsTreeNode):
            raise Exception("Invalid fs_object type")
        if not isinstance(self,type(fs_object)):
            return False
        if self.name!=fs_object.name:
            return False
        if isinstance(self.parent_dir,type(None)):
            return isinstance(fs_object.parent_dir,type(None))
        return self.parent_dir.is_same_path(fs_object.parent_dir)

    @property
    def parent_dir_non_dry(self,allow_hidden=False):
        from .directory import Directory
        if not self.is_same_path(Directory.NULL):
            if self.parent_dir.is_same_path(Directory.ROOT):
                return Directory("/",Directory.NULL)
            if (self.parent_dir.is_same_path(Directory.NULL)):
                return None
            return Directory(self.parent_dir.name,self.parent_dir.parent_dir,dry=False,allow_hidden=allow_hidden)
    
    @abc.abstractmethod
    def readFs(self,*args,**kwargs):
        return

    @property
    def ancestor_list(self):
        from .directory import Directory
        _parent=self
        _ancestors : list[Directory] = []
        while(not _parent.parent_dir.is_same_path(Directory.NULL)):
            _parent=_parent.parent_dir
            _ancestors.append(_parent)
        if not isinstance(_parent,FsTreeNode):
            raise Exception("Invalid parent type")
        return _ancestors

    @property
    def is_absolute(self):
        from .directory import Directory
        if len(self.ancestor_list)==0:
            return False
        highest_parent=self.ancestor_list.pop()
        return highest_parent.is_same_path(Directory.ROOT)

    @abc.abstractproperty
    def in_fs(self):
        return

    @abc.abstractmethod
    def updateFs(self,*args,**kwargs):
        return

    @abc.abstractmethod
    def deleteFs(self):
        return
