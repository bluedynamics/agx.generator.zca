Test agx.generator.zca
======================

Setup configuration and emulate main routine::

    >>> from zope.configuration.xmlconfig import XMLConfig

    >>> import agx.core
    >>> XMLConfig('configure.zcml', agx.core)()

    >>> from agx.core.main import parse_options

    >>> import os
    >>> modelpath = os.path.join(datadir, 'agx.generator.zca-sample.uml')

    >>> import pkg_resources
    >>> subpath = 'profiles/pyegg.profile.uml'
    >>> eggprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.pyegg', subpath)

    >>> subpath = 'profiles/zca.profile.uml'
    >>> zcaprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.zca', subpath)

    >>> modelpaths = [modelpath, eggprofilepath, zcaprofilepath]

    >>> outdir = os.path.join(datadir, 'agx.generator.zca-sample')
    >>> controller = agx.core.Controller()
    >>> target = controller(modelpaths, outdir)
    >>> target
    <Directory object '/.../agx.generator.zca/src/agx/generator/zca/testing/data/agx.generator.zca-sample' at ...>
