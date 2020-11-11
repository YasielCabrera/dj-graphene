# Dj Graphene

This package adds extra functionalities to graphene-django to make stuffs more in the "django way", writing less code and get more things done.

> **WARNING:** This is still in development and some things may not work properly. I will try to solve all the bugs ASAP but it may take time.

## Features

**Note:** By installing this package graphene and graphene-django will be available so all the features of those packages are also available.

- New base type: ModelObjectType
  - ModelObjectType allow to create new types with default permissions. The fields in this package only works with subtypes of ModelObjectType
- A straightforward but powerful permissions system (like DRF permissions)
- New fields: RelayConnectionField, RelayFilterConnectionField
- DjangoModelMutation
  - Allow to create easily create/update/delete mutations


## Types

For the following examples we will use these models:

```py
class Author(models.Model):
    name = models.CharField(max_length=100, blank=False)
    birthday = models.DateField()

class Book(models.Model):
    isbn = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=100, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
```

The types would look like this:

```py
class AuthorNode(ModelObjectType):

    class Meta:
        model = Author
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
        # we use RelayNode instead of graphene.relay.Node
        interfaces = (RelayNode, )
        permission_classes = (IsAuthenticated, )


class BookNode(ModelObjectType):

    class Meta:
        model = Book
        interfaces = (RelayNode, )
        permission_classes = (IsAuthenticated, )
```

## Queries

```py
class Query(graphene.ObjectType):
    author = RelayNode.Field(AuthorNode)
    authors = RelayFilterConnectionField(AuthorNode)

    book = RelayNode.Field(BookNode)
    books = RelayFilterConnectionField(BookNode)
```

## Mutations

```py
class NewAuthorMutation(DjangoModelMutation):
    class Meta:
        model = Author
        fields = ('name', 'birthday')
        permission_classes = (IsAuthenticated, )


class UpdateAuthorMutation(DjangoModelMutation):
    class Meta:
        model = Author
        permission_classes = (IsAuthenticated, )


class DeleteAuthorMutation(DjangoModelMutation):
    class Meta:
        model = Author
        fields = ['id']
        # required param to indicate that this is a delete mutation
        deleting = True
        # is_relay is used to translate GlobalId into Django IDs
        is_relay = True
        permission_classes = (IsAuthenticated, )


class Mutations(graphene.ObjectType):
    create_author = NewAuthorMutation.Field()
    update_author = UpdateAuthorMutation.Field()
    delete_author = DeleteAuthorMutation.Field()
```