# Copyright BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2

from zope.interface import implements
from zope.configuration.xmlconfig import XMLConfig
from agx.core.interfaces import IConfLoader
import agx.generator.uml
import agx.generator.zca

class ConfLoader(object):
    
    implements(IConfLoader)
    
    transforms = [
        'xmi2uml',
        'uml2fs',
    ]
    
    def __call__(self):
        XMLConfig('configure.zcml', agx.generator.uml)()
        XMLConfig('configure.zcml', agx.generator.zca)()