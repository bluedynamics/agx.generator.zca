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
    if zcmlpath!='configure.zcml':
#        import pdb;pdb.set_trace()
        
        if zcml.name=='configure.zcml':
            packname='.'+directory.name
            found_include = conf.filter(tag='include', attr='package', 
                                        value=packname)
            #add include directive if necessary
            if not found_include:
                include = SimpleDirective(name='include', parent=conf)
                include.attrs['package'] = packname
        else:
            found_include = conf.filter(tag='include', attr='file', 
                                        value=zcmlpath)
            #add include directive if necessary
            if not found_include:
                include = SimpleDirective(name='include', parent=conf)
                include.attrs['file'] = zcmlpath

        
    if directory not in token('pyeggs',False).directories:
        parentdir = directory.__parent__
        addZcmlRef(parentdir, conf)

def get_zcml(directory,zcmlname,nsmap=None):
    directory.factories['.zcml']=ZCMLFile
    if not zcmlname in directory:
        if nsmap:
            new=ZCMLFile(nsmap=nsmap)
        else:
            new=ZCMLFile()
        directory[zcmlname]=new
        res=new
    else:
        res=directory[zcmlname]
    return res

def set_zcml_namespace(directory,zcmlname,nsid,nspath):
    zcml=get_zcml(directory,zcmlname)
    zcml.nsmap['plone']='http://namespaces.plone.org/plone'
    zcml.nsmap[nsid]=nspath
    
def set_zcml_directive(directory,zcmlname,tag,attr,value,**kw):
    zcml=get_zcml(directory,zcmlname)
    directives=zcml.filter(tag=tag, attr=attr, value=value)
    if directives:
        directive=directives[0]
    else:
        directive=SimpleDirective(name=tag, parent=zcml)
            
    directive.attrs[attr]=value
        
    for k in kw:
        directive[k]=kw[k]
    
def zcml_include_package(directory):
    if not 'configure.zcml' in directory.parent:
        directory.parent['configure.zcml'] = ZCMLFile()
    zcml = directory.parent['configure.zcml']
    package = '.%s' % directory.name
    if not zcml.filter(tag='include', attr='package', value=package):
        include = SimpleDirective(name='include', parent=zcml)
        include.attrs['package'] = package