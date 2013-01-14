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


class PermitsScope(Scope):

    def __call__(self,node):
        return node.stereotype('zca:permits') is not None


class PermissionScope(Scope):

    def __call__(self,node):
        return node.stereotype('zca:permission') is not None


class SubscriberScope(Scope):

    def __call__(self,node):
        return node.stereotype('zca:subscriber') is not None


class EventForScope(Scope):

    def __call__(self,node):
        try:
            if node.stereotype('zca:for') is not None and \
                node.client.stereotype('zca:subscriber') is not None:
                return True
            else:
                return False
        except AttributeError:
            return False
