class PermissionsMixin:

    @classmethod
    def get_permissions(cls, info):
        return [permission(info) for permission in cls._meta.permission_classes]

    @classmethod
    def check_permissions(cls, info):
        for permission in cls.get_permissions(info):
            if not permission.has_permission():
                raise PermissionError('Permission denied.')
