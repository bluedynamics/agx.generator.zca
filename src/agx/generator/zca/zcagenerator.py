from agx.core import (
    handler,
    Scope,
    registerScope,
)
from node.ext.uml.interfaces import IInterface
from agx.generator.zca.scope import (
    UtilityScope,
    AdapterScope,
)

registerScope('zcainterface', 'uml2fs', [IInterface], Scope)

@handler('zcainterface', 'uml2fs', 'zcagenerator', 'zcainterface')
def zcainterface(self, source, target):
    """Create zope interface.
    """
    print 'zcainterface'
    print source, target

registerScope('zcautility', 'uml2fs', None, UtilityScope)

@handler('zcautility', 'uml2fs', 'zcagenerator', 'zcautility')
def zcautility(self, source, target):
    """Create zope utility.
    """
    print 'zcautility'
    print source, target

registerScope('zcaadapter', 'uml2fs', None, AdapterScope)

@handler('zcaadapter', 'uml2fs', 'zcagenerator', 'zcaadapter')
def zcaadapter(self, source, target):
    """Create zope adapter.
    """
    print 'zcaadapter'
    print source, target