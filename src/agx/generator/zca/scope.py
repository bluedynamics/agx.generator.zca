from agx.core import Scope

class UtilityScope(Scope):

    def __call__(self, node):
        return node.stereotype('zca:utility') is not None

class AdapterScope(Scope):

    def __call__(self, node):
        return node.stereotype('zca:adapter') is not None
    
class AdaptsScope(Scope):

    def __call__(self, node):
        return node.stereotype('zca:adapts') is not None
    