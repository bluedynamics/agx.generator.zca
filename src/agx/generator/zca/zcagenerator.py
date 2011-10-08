import os

from zope.component.interfaces import ComponentLookupError

from agx.core import (
    handler,
    Scope,
    registerScope,
    token
)
from agx.core.util import read_target_node, dotted_path
from agx.generator.pyegg.utils import class_base_name

from node.ext.python.utils import Imports
from node.ext.uml.interfaces import IInterface, IInterfaceRealization, IDependency
from node.ext.python.interfaces import IBlock, IDocstring


from node.ext import python
from node.ext.python.interfaces import IFunction
from node.ext.python.nodes import (
    Function,
    Block,
)

from node.ext.uml.utils import (
    Inheritance,
    TaggedValues,
    UNSET,
)

from agx.generator.zca.scope import (
    UtilityScope,
    AdapterScope,
    AdaptsScope,
)

from agx.generator.zca.utils import addZcmlRef

from node.ext.zcml import ZCMLNode
from node.ext.zcml import ZCMLFile
from node.ext.zcml import SimpleDirective
from node.ext.zcml import ComplexDirective
from node.ext.uml.utils import TaggedValues, UNSET

from agx.generator.pyegg.utils import (
    templatepath,
    set_copyright,
)


registerScope('zcainterface', 'uml2fs', [IInterface], Scope)
registerScope('zcarealize', 'uml2fs', [IInterfaceRealization], Scope)
registerScope('zcaadapts', 'uml2fs', None, AdaptsScope)

@handler('interfacegeneralization', 'uml2fs', 'connectorgenerator', 
         'zcainterface', order=10)
def interfacegeneralization(self, source, target):
    """Create generalization between interfaces .
    """

    inheritance = Inheritance(source)
    targetclass = read_target_node(source, target.target)
    if targetclass:
        tok=token(str(targetclass.uuid),True,depends_on=set())
    for obj in inheritance.values():
        tok.depends_on.add(read_target_node(obj.context, target.target))
        if not obj.context.name in targetclass.bases:
            targetclass.bases.append(obj.context.name)
            tgv = TaggedValues(obj.context)
            import_from = tgv.direct('import', 'pyegg:stub')
            if import_from is not UNSET:
                imp = Imports(targetclass.__parent__)
                imp.set(import_from, [[obj.context.name, None]])
        derive_from = read_target_node(obj.context, target.target)
        if not derive_from:
            continue
        if targetclass.__parent__ is not derive_from.__parent__:
            imp = Imports(targetclass.__parent__)
            imp.set(class_base_name(derive_from),
                    [[derive_from.classname, None]])

            
    if targetclass and not targetclass.bases:
        targetclass.bases.append('Interface')
    

@handler('zcainterface', 'uml2fs', 'hierarchygenerator', 
         'zcainterface', order=20)
def zcainterface(self, source, target):
    """Create zope interface.
    """
    if source.stereotype('pyegg:stub') is not None:
        return
    name = source.name
    module = target.anchor
    imp = Imports(module)
    imp.set('zope.interface', [['Interface', None]])

    set_copyright(source, module)
    if module.classes(name):
        class_ = module.classes(name)[0]
    else:
        class_ = python.Class(name)
        module[name] = class_

#    if not class_.bases:
#        class_.bases.append('Interface')

    target.finalize(source, class_)


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

@handler('zcaadapter_py_imports', 'uml2fs', 'zcagenerator', 'zcaadapter')
def zcaadapter(self, source, target):
    pass

@handler('zcaadapter_zcml', 'uml2fs', 'zcagenerator', 'zcaadapter')
def zcaadapter_zcml(self, source, target):
    """Create zope adapter.
    """
#    import pdb;pdb.set_trace()
    #print 'zcaadapter'
    #print source, target

@handler('zcaadapts', 'uml2fs', 'zcagenerator', 'zcaadapts', order=10)
def zcaadapts(self, source, target):
    tok = token(str(source.client.uuid), True)
    pack = source.parent
    
    target = read_target_node(pack, target.target)
    if isinstance(target, python.Module):
        targetdir = target.parent
    else:
        targetdir = target
    
    path = targetdir.path
    path.append('adapters.zcml')
    fullpath = os.path.join(*path)
    if 'adapters.zcml' not in targetdir.keys():
        zcml = ZCMLFile(fullpath)
        targetdir['adapters.zcml'] = zcml
    else:
        zcml = targetdir['adapters.zcml']

    addZcmlRef(targetdir, zcml)
        
    _for = dotted_path(source.supplier)
    factory = dotted_path(source.client)
    tgv = TaggedValues(source.client)
    name = tgv.direct('name', 'zca:adapter')
    
    found_adapts = zcml.filter(tag='adapter', attr='factory', value=factory)
    
    if found_adapts:
        adapts = found_adapts[0]
    else:     
        adapts = SimpleDirective(name='adapter', parent=zcml)
    

    adapts.attrs['for'] = _for
    if not name is UNSET:
        adapts.attrs['name'] = name
        
    adapts.attrs['factory'] = factory

@handler('zcarealize', 'uml2fs', 'connectorgenerator', 'zcarealize',order=10)
def zcarealize(self, source, target):
    klass = source.implementingClassifier
    ifacename = source.contract.name
    targetclass = read_target_node(klass, target.target)
    tok = token(str(klass.uuid), True, realizes=[])
    tok.realizes.append(ifacename)
    targetinterface = read_target_node(source.contract, target.target)
    
    #import the interface
    tgv = TaggedValues(source.contract)
    import_from = tgv.direct('import', 'pyegg:stub')
    imp = Imports(targetclass.__parent__)

    if targetinterface:    
        tok=token(str(targetclass.uuid),True,depends_on=set())
        tok.depends_on.add(targetinterface)

    #if (targetinterface is None -> Stub) or targetinterface is in another module: import
    if not targetinterface or targetclass.__parent__ is not targetinterface.__parent__:
        if import_from is not UNSET: #we have a stub interface
            basepath = import_from
            imp.set(basepath, [[source.contract.name, None]])
        else:
            basepath = class_base_name(targetinterface)
            imp.set(basepath, [[targetinterface.classname, None]])
        


@handler('zcarealize_finalize', 'uml2fs', 'zcagenerator', 'pyclass')
def zcarealize_finalize(self, source, target):
#   get the collected realizes 
    klass = source
    try:
        tok = token(str(klass.uuid), False)
        ifacenames = tok.realizes
        targetclass = read_target_node(klass, target.target)
        imptext = 'implements(%s)' % ','.join(ifacenames)
        docstrings = targetclass.filteredvalues(IDocstring)
        
        module=targetclass.__parent__
        imp = Imports(module)
        imp.set('zope.interface', [['implements', None]])
        #delete all implements stmts
        try:
            blocks = targetclass.filteredvalues(IBlock)
            for b in blocks:
                if b.text.strip().startswith('implements('):
                    del targetclass[str(b.uuid)]
            #XXX: soll repased werden
        except KeyError:
            print 'error during delete'
            pass
        
        block = Block(imptext)
        block.__name__ = 'implements'
        targetclass.insertfirst(block)

        if docstrings:
            imp = targetclass.detach('implements')
            targetclass.insertafter(imp, docstrings[0])

        # vors __init__
    except ComponentLookupError:
        #keine realize parents vorhanden
        pass
    

