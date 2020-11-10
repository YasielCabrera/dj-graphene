class BasePermission(object):
    
    def __init__(self, info, *args, **kwargs):
        self.info = info

    def has_permission(self):
        raise NotImplementedError()


class AllowAny(BasePermission):
    
    def has_permission(self):
        return True


class IsAuthenticated(BasePermission):
    
    def has_permission(self):
        return self.info.context.user and self.info.context.user.is_authenticated


class IsAdminUser(BasePermission):
    
    def has_permission(self):
        return self.info.context.user and self.info.context.user.is_staff
