# Copyright BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2

import agx.generator.zca
from zope.interface import implements
from agx.core.interfaces import IProfileLocation

class ProfileLocation(object):
    implements(IProfileLocation)
    name = u'zca.profile.uml'
    package = agx.generator.zca