import os
from zope.component.interfaces import ComponentLookupError
from agx.core import (
    handler,
    Scope,
    registerScope,
    token
)
from agx.core.util import (
    read_target_node,
    dotted_path,
)
from node.ext.uml.interfaces import (
    IInterface,
    IInterfaceRealization,
    IDependency,
)
from node.ext.uml.utils import (
    Inheritance,
    TaggedValues,
    UNSET,
)
from node.ext.python.interfaces import (
    IBlock,
    IDocstring,
)
from node.ext import python
from node.ext.python.interfaces import (
    IFunction,
    IModule,
)
from node.ext.python.nodes import (
    Function,
    Block,
)
from node.ext.python.utils import Imports
from agx.generator.zca.scope import (
    UtilityScope,
    AdapterScope,
    AdaptsScope,
    PermitsScope,
    PermissionScope,
)
from agx.generator.zca.utils import addZcmlRef
from node.ext.zcml import (
    ZCMLNode,
    ZCMLFile,
    SimpleDirective,
    ComplexDirective,
)
from node.ext.uml.utils import (
    TaggedValues,
    UNSET,
)
from agx.generator.pyegg.utils import (
    class_base_name,
    templatepath,
    set_copyright,
)


registerScope('zcainterface', 'uml2fs', [IInterface], Scope)
registerScope('zcarealize', 'uml2fs', [IInterfaceRealization], Scope)
registerScope('zcaadapts', 'uml2fs', None, AdaptsScope)
registerScope('zcapermits', 'uml2fs', None, PermitsScope)
registerScope('zcapermission', 'uml2fs', None, PermissionScope)


@handler('interfacegeneralization', 'uml2fs', 'connectorgenerator',
         'zcainterface', order=10)
def interfacegeneralization(self, source, target):
    """Create generalization between interfaces .
    """
    inheritance = Inheritance(source)
    targetclass = read_target_node(source, target.target)
    if targetclass:
        tok = token(str(targetclass.uuid), True, depends_on=set())
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
    if source.stereotype('pyegg:function'):
        # XXX: <<function>> <<adapter>> on class
        return
    adapter_class = read_target_node(source, target.target)
    exists = False
    for function in adapter_class.filteredvalues(IFunction):
        if function.functionname == '__init__':
            exists = function
            break
    if not exists:
        tok = token(str(adapter_class.uuid), False)
        adapts = token(str(source.uuid), False).adapts
        if len(adapts)==1:
            params=['context']
        else:
            params=[]
            for cl in adapts:
                if cl.name.startswith('I'):
                    params.append(cl.name[1:].lower())
                else:
                    params.append(cl.name.lower())
        func = Function('__init__')
        func.args = params
        block = Block()
        for param in params:
            block.lines.append('self.%s = %s' % (param, param))
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


@handler('zcaadaptscollect', 'uml2fs', 'connectorgenerator',
         'zcaadapts', order=10)
def zcaadaptscollect(self, source, target):
    pack = source.parent
    adaptee = source.supplier
    adapter = source.client
    target = read_target_node(pack, target.target)
    targetadaptee = read_target_node(adaptee, target)
    tok = token(str(adapter.uuid), True, adapts=[])
    adapteetok = token(str(adaptee.uuid),True,fullpath=None)
    if targetadaptee:
        adapteetok.fullpath = dotted_path(adaptee)
    else: #its a stub
        adapteetok.fullpath = '.'.join(
            [TaggedValues(adaptee).direct('import', 'pyegg:stub'), adaptee.name])
    if isinstance(target, python.Module):
        targetdir = target.parent
    else:
        targetdir = target
#    print 'adaptcollect:',adaptee.name
    tok.adapts.append(adaptee)


@handler('zcaadapts', 'uml2fs', 'zcagenerator', 'zcaadapter', order=20)
def zcaadapts(self, source, target):
    adapter = source
    if adapter.stereotype('pyegg:function'):
        # XXX: <<function>> <<adapter>> on class
        return
    tok = token(str(adapter.uuid), True)
    pack = source.parent
    target = read_target_node(pack, target.target)
    targetclass = read_target_node(adapter, target)
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
    targettok = token(str(targetclass.uuid), True, realizes=[], provides=None)
    _for = [token(str(adaptee.uuid), False).fullpath for adaptee in tok.adapts]
    factory = dotted_path(adapter)
    tgv = TaggedValues(adapter)
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
    #write the provides which is collected in the zcarealize handler
    if len(targettok.realizes) == 1:
        provides = targettok.realizes[0]
    else:
        provides = targettok.provides
    adapts.attrs['provides'] = provides['path']
    if hasattr(tok,'permission'):
        adapts.attrs['permission']=tok.permission


@handler('zcarealize', 'uml2fs', 'connectorgenerator', 'zcarealize', order=10)
def zcarealize(self, source, target):
    klass = source.implementingClassifier
    if klass.stereotype('pyegg:function'):
        # XXX: <<function>> <<adapter>> on class
        return
    
    ifacename = source.contract.name
    targetclass = read_target_node(klass, target.target)
    targetinterface = read_target_node(source.contract, target.target)
    tok = token(str(targetclass.uuid), True, realizes=[], provides=None)
    
    ifdef = {'name':source.contract.name}
    if targetinterface:
        ifdef['path'] = dotted_path(source.contract)
    else: #then its a stub
        tgv=TaggedValues(source.contract)
        impf=tgv.direct('import', 'pyegg:stub')
        if not impf:
            raise ValueError,'Stub class %s needs a TaggedValue for "import"' % dotted_path(klass)
        ifdef['path'] = '.'.join([impf, ifdef['name']])

    tok.realizes.append(ifdef)
#    print 'zcarealize:',klass.name,source.contract.name
    if source.stereotype('zca:provides'):
        tok.provides = ifdef
    
    #import the interface
    tgv = TaggedValues(source.contract)
    import_from = tgv.direct('import', 'pyegg:stub')
    imp = Imports(targetclass.__parent__)

    if targetinterface:    
        tok = token(str(targetclass.uuid), True, depends_on=set())
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
        targetclass = read_target_node(klass, target.target)
        
        if not targetclass: #stub
            return
        
        targettok=token(str(targetclass.uuid), False)
        if not hasattr(targettok,'realizes'):
            return #class has no interfaces
        ifacenames = [r['name'] for r in targettok.realizes]
        imptext = 'implements(%s)' % ','.join(ifacenames)
        docstrings = targetclass.filteredvalues(IDocstring)
        
        module = targetclass.__parent__
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
    
@handler('createpermission', 'uml2fs', 'connectorgenerator', 'zcapermission')
def createpermission(self, source, target):
    
    targetclass=read_target_node(source, target.target)
    module=targetclass.parent
    targetdir=module.parent

    path=class_base_name(targetclass)
    
    #prevent python class from being generated
    sts=[st.name for st in source.stereotypes]
    if 'zca:permission' in sts and len(sts)==1: #only if no other steroetypes are attached
        #class also has to be deleted from __init__
        init=targetdir['__init__.py']
        for imp in init.imports():
            if imp.fromimport==path and imp.names[0][0]==source.name:
                del init[imp.__name__]
        del module[targetclass.__name__]

    #and now write the permission definition into confure.zcml
    zcmlpath = targetdir.path
    zcmlpath.append('configure.zcml')
    fullpath = os.path.join(*zcmlpath)

    if 'configure.zcml' not in targetdir.keys():
        zcml = ZCMLFile(fullpath)
        targetdir['configure.zcml'] = zcml
    else:
        zcml = targetdir['configure.zcml']
    addZcmlRef(targetdir, zcml)
    
    id=TaggedValues(source).direct('id', 'zca:permission')
    
    if id is UNSET:
        permid=dotted_path(source)
    else:
        permid=id
        
    found_directives = zcml.filter(tag='permission', attr='id', value=permid)
    if found_directives:
        directive = found_directives[0]
    else:     
        directive = SimpleDirective(name='permission', parent=zcml)

    directive.attrs['id']=permid
    title=TaggedValues(source).direct('title', 'zca:permission')
    if not title is UNSET:
        directive.attrs['title']=title

    description=TaggedValues(source).direct('description', 'zca:permission')
    if not description is UNSET:
        directive.attrs['description']=description
    
    
@handler('collectpermissions', 'uml2fs', 'connectorgenerator', 'zcapermits')
def collectpermissions(self, source, target):
    permid=dotted_path(source.supplier)
    id=TaggedValues(source.supplier).direct('id', 'zca:permission')
    
    if not id is UNSET:
        permid=id

    tok=token(str(source.client.uuid),True,permission=permid)
    
