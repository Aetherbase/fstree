from typing import Iterable
import os
from .fs_tree_node import FsTreeNode
from .file import File
class Directory(FsTreeNode):
    ROOT = None
    NULL = None
    def __init__(self, dirname: str, parent_dir , children = None,dry = False,allow_hidden=False,dry_files=True):
        super(Directory,self).__init__(dirname,parent_dir,allow_hidden)
        self.dry=dry
        self.children=dict()
        self.dry_files=dry_files
        if self.dry!=True:
            self.readFs(dry_files=dry_files,allow_hidden=allow_hidden)
            if type(children)==Iterable:
                self.children.clear()
                for _child in children:
                    self.add_child(_child)

    def add_child(self,fs_object,type_hint = None):
        if isinstance(fs_object,FsTreeNode):
            fs_object.set_parent(self)
        elif type(fs_object)==str:
            FsTreeNode.from_path(fs_object,type_hint=type_hint).set_parent(self)
        else:
            raise Exception("Invalid child type")

    @staticmethod
    def from_path(path,children = None,dry = False,allow_hidden=False,dry_files=True):
        return(FsTreeNode.from_path(path,type_hint=Directory,children=children,dry=dry,allow_hidden=allow_hidden,dry_files=dry_files))
    
    def copyTo(self,dir,name=None, update_fs=False,allow_hidden=False,ignore = []):
        if type(name)==type(None):
            name=self.name
        cp_dir=Directory(name=name,parent_dir=dir,children=self.children,allow_hidden=allow_hidden)
        if update_fs==True:
            cp_dir.updateFs(update_childs=True)
        return cp_dir
    
    def list_children(self):
        return list(self.children.keys())
    
    def list_files(self):
        file_list=[]
        for _child in self.children.values():
            if type(_child)==File:
                file_list.append(_child.name)
        return file_list

    def list_dirs(self):
        dir_list=[]
        for _child in self.children.values():
            if type(_child)==Directory:
                dir_list.append(_child.name)
        return dir_list

    def get_child(self,child_name :str):
        if self.dry:
            raise Exception("Cannot fetch children from dry directory")
        if child_name in self.children.keys():
                return self.children[child_name]
        raise Exception(f"Directory at {self.path} has no child {child_name}.")

    def __getitem__(self,_key : str):
        return self.get_child(_key)
        
    @property
    def in_fs(self):
        return(os.path.isdir(self.path))

    def readFs(self,allow_hidden=False,dry=None,dry_files=True):
        if type(dry)==bool:
            self.dry=dry
        if (self.dry!=True) and (self.in_fs==True):
                self.children.clear()
                listdir = os.listdir(self.path)
                for elem in listdir:
                    elem_path=os.path.join(self.path,elem)
                    if os.path.isfile(elem_path) and not (not allow_hidden and elem.startswith(".")):
                        self.children[elem]=File(elem,self,dry=dry_files)
                    if os.path.isdir(elem_path) and not (not allow_hidden and elem.startswith(".")):
                        self.children[elem]=Directory(elem,self,allow_hidden=allow_hidden,dry_files=dry_files)
        else:
            self.children.clear()

    def updateFs(self,update_children = False,allow_hidden=False):
        if type(self.parent_dir)!=type(None):
            self.parent_dir.updateFs()
        if (not self.in_fs) :
            os.mkdir(self.path)
            if (not self.dry) and update_children:
                for _child in self.children.values():
                    if(type(_child)==File):
                        _child.updateFs()
                    elif(type(_child)==Directory):
                        _child.updateFs(update_children)
        else:
            if (not self.dry) and update_children:
                _childset=set()
                listdir = os.listdir(self.path)
                for elem in listdir:
                    if not (not allow_hidden and elem.startswith(".")):
                        if os.path.isdir(os.path.join(self.path,elem)):
                            _childset.add(elem)
                        elif os.path.isfile(os.path.join(self.dirpath,elem)):
                            _childset.add(elem)
                for _d in _childset-set(self.children.keys()):
                    self.children[_d].deleteFs()
                for _child in self.children.values():
                    if(type(_child)==File):
                        _child.updateFs()
                    elif(type(_child)==Directory):
                        _child.updateFs(update_children)

    def deleteFs(self):
        if not self.dry:
            for _child in self.children.values():
                _child.deleteFs()
        if self.in_fs:
            os.removedirs(self.path)

Directory.NULL=Directory("",None,dry=True)
Directory.ROOT=Directory("/",Directory.NULL,dry=True)
