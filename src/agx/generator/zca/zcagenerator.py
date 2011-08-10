import os

from agx.core import (
    handler,
    Scope,
    registerScope,
    token
)
from agx.core.util import read_target_node, dotted_path
from node.ext.uml.interfaces import IInterface,IInterfaceRealization,IDependency
from node.ext.python.interfaces import IFunction
from node.ext.python.nodes import (
    Function,
    Block,
)

from agx.generator.zca.scope import (
    UtilityScope,
    AdapterScope,
    AdaptsScope,
)

from node.ext.zcml import ZCMLNode
from node.ext.zcml import ZCMLFile
from node.ext.zcml import SimpleDirective
from node.ext.zcml import ComplexDirective


registerScope('zcainterface', 'uml2fs', [IInterface], Scope)
registerScope('zcarealize', 'uml2fs', [IInterfaceRealization], Scope)
registerScope('zcaadapts', 'uml2fs', None, AdaptsScope)

@handler('zcainterface', 'uml2fs', 'zcagenerator', 'zcainterface')
def zcainterface(self, source, target):
    """Create zope interface.
    """
    #print 'zcainterface'
    #print source, target

registerScope('zcautility', 'uml2fs', None, UtilityScope)

@handler('zcautility', 'uml2fs', 'zcagenerator', 'zcautility')
def zcautility(self, source, target):
    """Create zope utility.
    """
    #print 'zcautility'
    #print source, target

registerScope('zcaadapter', 'uml2fs', None, AdapterScope)

@handler('zcaadapterdefaultinit', 'uml2fs', 'zcagenerator', 'zcaadapter')
def zcaadapterdefaultinit(self, source, target):
    """Set default __init__ function on adapter class if not present yet.
    """
    adapter_class = read_target_node(source, target.target)
    exists = False
    for function in adapter_class.filteredvalues(IFunction):
        if function.functionname == '__init__':
            exists = function
            break
    if not exists:
        func = Function('__init__')
        func.args.append('context')
        block = Block()
        block.text = 'self.context = context'
        func[block.uuid] = block
        adapter_class[func.uuid] = func

@handler('zcaadapter_py_imports', 'uml2fs','zcagenerator','zcaadapter')
def zcaadapter(self, source, target):
    pass

@handler('zcaadapter_zcml', 'uml2fs', 'zcagenerator', 'zcaadapter')
def zcaadapter_zcml(self, source, target):
    """Create zope adapter.
    """
#    import pdb;pdb.set_trace()
    #print 'zcaadapter'
    #print source, target

@handler('zcarealize', 'uml2fs','zcagenerator','zcaadapter')
def zcarealize(self, source, target):
    pass

@handler('zcaadapts', 'uml2fs','zcagenerator','zcaadapts')
def zcaadapts(self, source, target):
    tok=token(str(source.client.uuid),True)
    pack=source.parent
    targetdir=read_target_node(pack, target.target)
    path=targetdir.path
    path.append('adapters.zcml')
    fullpath=os.path.join(*path)
    zcml=ZCMLFile(fullpath)
    targetdir['adapters.zcml']=zcml
    _for=dotted_path(source.supplier)
    factory=dotted_path(source.client)
    name='%s_adapts_%s' %(factory,_for)
    
    found_adapts=zcml.filter(tag='adapter',attr='name',value=name)
    
    if found_adapts:
        adapts=found_adapts[0]
    else:     
        adapts = SimpleDirective(name='adapter', parent=zcml)
        
    adapts.attrs['for'] = _for
    adapts.attrs['name'] = name
    adapts.attrs['factory'] = factory

