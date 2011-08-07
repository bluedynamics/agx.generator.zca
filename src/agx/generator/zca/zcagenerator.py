from agx.core import (
    handler,
    Scope,
    registerScope,
)
from agx.core.util import read_target_node
from node.ext.uml.interfaces import IInterface
from node.ext.python.interfaces import IFunction
from node.ext.python.nodes import (
    Function,
    Block,
)

from agx.generator.zca.scope import (
    UtilityScope,
    AdapterScope,
)

registerScope('zcainterface', 'uml2fs', [IInterface], Scope)

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
        func.args.append('self', 'context')
        block = Block()
        block.text = 'self.context = context'
        func[block.uuid] = block
        adapter_class[func.uuid] = func

@handler('zcaadapter', 'uml2fs', 'zcagenerator', 'zcaadapter')
def zcaadapter(self, source, target):
    """Create zope adapter.
    """
    #print 'zcaadapter'
    #print source, target