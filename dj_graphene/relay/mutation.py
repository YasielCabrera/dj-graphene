from collections import OrderedDict

import graphene
from django.forms import models as model_forms
from django.forms.models import model_to_dict
from graphene import Field, InputField
from graphene.relay.mutation import ClientIDMutation
from graphene.types.mutation import MutationOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene_django.forms.converter import convert_form_field
from graphene_django.registry import get_global_registry
from graphene_django.types import ErrorType
from graphql_relay.node.node import from_global_id

from ..mixins import PermissionsMixin
from .utils import normalize_global_ids

ALL_FIELDS = '__all__'


def fields_for_form(form, model_fields):
    fields = OrderedDict()
    for name, field in form.fields.items():
        if model_fields != ALL_FIELDS and name not in model_fields:
            continue

        fields[name] = convert_form_field(field)
    return fields


class BaseDjangoFormMutation(ClientIDMutation):
    class Meta:
        abstract = True

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        form = cls.get_form(root, info, **input)

        if form.is_valid():
            return cls.perform_mutate(form, info)
        else:
            errors = ErrorType.from_errors(form.errors)

            return cls(errors=errors, **form.data)

    @classmethod
    def get_form(cls, root, info, **input):
        form_kwargs = cls.get_form_kwargs(root, info, **input)
        return cls._meta.form_class(**form_kwargs)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = {"data": input}

        pk = input.pop("id", None)
        if pk:
            instance = cls._meta.model._default_manager.get(pk=pk)
            kwargs["instance"] = instance
            if instance:
                # prevent erase non sended fields data
                initial = model_to_dict(instance, fields=[
                    field.name for field in instance._meta.fields])
                kwargs["data"] = {**initial, **input}

        return kwargs


class DjangoFormMutationOptions(MutationOptions):
    form_class = None
    permission_classes = None


# Not tested
class DjangoFormMutation(PermissionsMixin, BaseDjangoFormMutation):
    class Meta:
        abstract = True

    errors = graphene.List(ErrorType)

    @classmethod
    def __init_subclass_with_meta__(
        cls, form_class=None, permission_classes=None, only_fields=(), exclude_fields=(), **options
    ):

        if not form_class:
            raise Exception("form_class is required for DjangoFormMutation")

        form = form_class()
        input_fields = fields_for_form(form, only_fields, exclude_fields)
        output_fields = fields_for_form(form, only_fields, exclude_fields)

        if permission_classes is None:
            permission_classes = ()

        _meta = DjangoFormMutationOptions(cls)
        _meta.form_class = form_class
        _meta.permission_classes = permission_classes
        _meta.fields = yank_fields_from_attrs(output_fields, _as=Field)

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super(DjangoFormMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, input_fields=input_fields, **options
        )

    @classmethod
    def perform_mutate(cls, form, info):
        cls.check_permissions(info)

        form.save()
        return cls(errors=[], **form.cleaned_data)


class DjangoModelMutationOptions(DjangoFormMutationOptions):
    model = None
    fields = None
    return_field_name = None
    deleting = False
    is_relay = False


class DjangoModelMutation(PermissionsMixin, BaseDjangoFormMutation):
    class Meta:
        abstract = True

    errors = graphene.List(ErrorType)

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        form_class=None,
        model=None,
        fields=ALL_FIELDS,
        permission_classes=None,
        return_field_name=None,
        deleting=False,
        is_relay=False,
        **options
    ):
        if form_class and not model:
            model = form_class._meta.model

        if not model:
            raise Exception("model is required for DjangoModelMutation")

        if not form_class:
            form_class = model_forms.modelform_factory(model, fields=fields)

        input_fields = {}
        if not deleting:
            form = form_class()
            input_fields = fields_for_form(form, fields)

        if fields == ALL_FIELDS or "id" in fields or deleting:
            if is_relay:
                input_fields["id"] = graphene.GlobalID()
            else:
                input_fields["id"] = graphene.ID()

        registry = get_global_registry()
        model_type = registry.get_type_for_model(model)
        if not model_type:
            raise Exception("No type registered for model: {}".format(model.__name__))

        if not return_field_name:
            model_name = model.__name__
            return_field_name = model_name[:1].lower() + model_name[1:]

        output_fields = OrderedDict()
        output_fields[return_field_name] = graphene.Field(model_type)

        _meta = DjangoModelMutationOptions(cls)
        _meta.form_class = form_class
        _meta.fields = fields
        _meta.model = model
        _meta.permission_classes = permission_classes or ()
        _meta.return_field_name = return_field_name
        _meta.deleting = deleting
        _meta.is_relay = is_relay
        _meta.fields = yank_fields_from_attrs(output_fields, _as=Field)

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super(DjangoModelMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, input_fields=input_fields, **options
        )

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if cls._meta.is_relay:
            input = normalize_global_ids(cls._meta.model, input)

        cls.check_permissions(info)
        
        if cls._meta.deleting:
            id = input.get("id")
            return cls.perform_delete_mutate(info, id)

        form = cls.get_form(root, info, **input)

        if form.is_valid():
            return cls.perform_mutate(form, info)
        else:
            errors = ErrorType.from_errors(form.errors)

            return cls(errors=errors)

    @classmethod
    def perform_mutate(cls, form, info):
        obj = form.save()
        kwargs = {cls._meta.return_field_name: obj}
        return cls(errors=[], **kwargs)

    @classmethod
    def perform_delete_mutate(cls, info, id):
        try:
            obj = cls._meta.model._default_manager.get(pk=id)
            obj.delete()
            kwargs = {cls._meta.return_field_name: obj}
            return cls(errors=[], **kwargs)
        except cls._meta.model.DoesNotExist:
            return cls(errors=ErrorType.from_errors({'id': ['Not found.']}))
