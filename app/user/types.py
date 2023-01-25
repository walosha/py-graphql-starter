import graphene
from graphene_file_upload.scalars import Upload
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination
from graphene_django_extras import (DjangoListObjectType, DjangoObjectType,
                                    DjangoInputObjectType)
from .models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        description = "Type definition for a single user"
        filter_fields = {
            "id": ("exact", ),
            "email": ("exact", ),
            "lastname": ("icontains", "iexact"),
            "firstname": ("icontains", "iexact"),
        }

    def resolve_image(self, info):
        if self.image:
            return self.image.url
        return None


class UserListType(DjangoListObjectType):
    class Meta:
        description = "Type definition for User list"
        model = User
        queryset = User.objects.filter(verified=True)
        # ordering can be: string, tuple or list
        pagination = LimitOffsetGraphqlPagination(
            default_limit=25, ordering="-email")
        filter_fields = {
            "id": ("exact", ),
            "email": ("exact", ),
            "lastname": ("icontains", "iexact"),
            "firstname": ("icontains", "iexact"),
        }


class SignupRoleEnum(graphene.Enum):
    BASIC = 'BASIC'
    ADMIN = 'ADMIN'


class VerifyTokenOutputType(graphene.ObjectType):
    email = graphene.String()
    is_valid = graphene.Boolean()


class RegisterUserInputType(graphene.InputObjectType):
    # email_verify_token = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    firstname = graphene.String(required=True)
    lastname = graphene.String(required=True)
    phone = graphene.String(required=True)
    company = graphene.UUID()
    # role = SignupRoleEnum()
    image = Upload()


class ResponseHandler(graphene.ObjectType):
    messages = graphene.String(required=True)


class UserInputType(DjangoInputObjectType):
    class Meta:
        description = "User InputType definition to use as input on an Arguments class on traditional Mutations "
        model = User


class RegisterUserOutputType(graphene.ObjectType):
    id = graphene.UUID(required=True)
    email = graphene.String(required=True)
    firstname = graphene.String(required=True)
    lastname = graphene.String(required=True)
    access_token = graphene.String(required=True)
    # role = graphene.String(required=True)


class UserListOutputType(graphene.ObjectType):
    total_count = graphene.Int()
    results = graphene.List(UserType)
