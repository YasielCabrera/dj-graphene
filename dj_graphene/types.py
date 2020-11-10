
from graphene.types.objecttype import ObjectType, ObjectTypeOptions
from graphene_django.types import DjangoObjectType, DjangoObjectTypeOptions

from .mixins import PermissionsMixin
from .permissions import BasePermission


class ModelObjectTypeOptions(DjangoObjectTypeOptions):
    permission_classes = None


class ModelObjectType(PermissionsMixin, DjangoObjectType):

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        permission_classes=None,
        _meta=None,
        **options
    ):
        if not _meta:
            _meta = ModelObjectTypeOptions(cls)

        if permission_classes is None:
            permission_classes = ()

        assert isinstance(permission_classes, (list, tuple)), (
            'The permissions must be a list or tuple. Got %s' % type(permission_classes).__name__
        )
        assert not any([not issubclass(permission, BasePermission) for permission in permission_classes]), (
            'One or many provided permission are not a subclass of BasePermission.'
        )
        
        _meta.permission_classes = permission_classes

        super(ModelObjectType, cls).__init_subclass_with_meta__(
            _meta=_meta, **options
        )

    class Meta:
        abstract = True
