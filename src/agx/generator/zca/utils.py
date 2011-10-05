import os 

from agx.core import (
    handler,
    Scope,
    registerScope,
    token
)
from node.ext.zcml import ZCMLNode
from node.ext.zcml import ZCMLFile
from node.ext.zcml import SimpleDirective
from node.ext.zcml import ComplexDirective
from node.ext.uml.utils import TaggedValues, UNSET

confname='configure.zcml'
def relpath(self,other):
    assert self.path==other.path[:len(self.path)],'other must be a subpath of self'
    return '/'.join(other.path[len(self.path):])

def addZcmlRef(directory, zcml):
    ''' adds a reference to a zcml file and implicitly taks care for creating a configure.zcml'''
    # zcmls zamsammeln, um zu wissen, was vom configure.zcml includiert werden soll
        
    path = directory.path
    path.append(confname)
    fullpath = os.path.join(*path)
    if confname not in directory.keys():
        conf = ZCMLFile(fullpath)
        directory[confname] = conf
    else:
        conf = directory[confname]

    zcmlpath=relpath(directory,zcml)
    
    found_include = conf.filter(tag='include', attr='file', value=zcmlpath)
    
    #add include directive if necessary
    if not found_include:
        include = SimpleDirective(name='include', parent=conf)
        include.attrs['file']=zcmlpath
    
    if directory not in token('pyeggs',False).directories:
        parentdir=directory.__parent__
        addZcmlRef(parentdir,conf)