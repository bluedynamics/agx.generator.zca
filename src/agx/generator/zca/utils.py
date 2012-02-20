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


confname = 'configure.zcml'

def relpath(self,other):
    assert self.path == other.path[:len(self.path)], \
           'other must be a subpath of self'
    return '/'.join(other.path[len(self.path):])


def addZcmlRef(directory, zcml):
    """Adds a reference to a zcml file and implicitly taks care for creating 
    a configure.zcml"""
    # zcmls zamsammeln, um zu wissen, was vom configure.zcml includiert 
    # werden soll
    path = directory.path
    path.append(confname)
    #fullpath = os.path.join(*path)
    if confname not in directory.keys():
        #conf = ZCMLFile(fullpath)
        conf = ZCMLFile()
        directory[confname] = conf
    else:
        conf = directory[confname]

    zcmlpath = relpath(directory,zcml)
    if zcml.name!='configure.zcml':
        found_include = conf.filter(tag='include', attr='file', value=zcmlpath)
        #add include directive if necessary
        if not found_include:
            include = SimpleDirective(name='include', parent=conf)
            include.attrs['file'] = zcmlpath
    else:
        packname="."+directory.name
        found_include = conf.filter(tag='include', attr='package', value=packname)
        #add include directive if necessary
        if not found_include:
            include = SimpleDirective(name='include', parent=conf)
            include.attrs['package'] = packname

        
    if directory not in token('pyeggs',False).directories:
        parentdir = directory.__parent__
        addZcmlRef(parentdir, conf)


def zcml_include_package(directory):
    import pdb;pdb.set_trace()
    if not 'configure.zcml' in directory.parent:
        directory.parent['configure.zcml'] = ZCMLFile()
    zcml = directory.parent['configure.zcml']
    package = '.%s' % directory.name
    if not zcml.filter(tag='include', attr='package', value=package):
        include = SimpleDirective(name='include', parent=zcml)
        include.attrs['package'] = package