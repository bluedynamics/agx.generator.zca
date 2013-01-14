import agx.generator.zca
from zope.interface import implementer
from agx.core.interfaces import IProfileLocation


@implementer(IProfileLocation)
class ProfileLocation(object):
    name = u'zca.profile.uml'
    package = agx.generator.zca
