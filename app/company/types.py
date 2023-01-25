import graphene
from graphql import GraphQLError
from graphene_file_upload.scalars import Upload
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination
from graphene_django_extras import DjangoListObjectType, DjangoObjectType,  DjangoInputObjectType
from .models import Company


class CompanyType(DjangoObjectType):
    class Meta:
        model = Company
        fields = '__all__'
        description = "Type definition for a single company"
        filter_fields = {
            "id": ("exact", ),
            "name": ("icontains", "iexact"),
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('Permission Denied')
        return queryset.filter(created_by=info.context.user)

    def resolve_logo(self, info):
        if self.logo:
            return self.logo.url
        return None


class CompanyListType(DjangoListObjectType):
    class Meta:
        description = "Type definition for Company list"
        model = Company
        queryset = Company.objects.filter()
        # ordering can be: string, tuple or list
        pagination = LimitOffsetGraphqlPagination(
            default_limit=20, ordering="-name")
        filter_fields = {
            "id": ("exact", ),
            "name": ("icontains", "iexact"),
        }


class CompanyInputType(graphene.InputObjectType):
    name = graphene.String(required=True)
    url = graphene.String(required=True)
    address = graphene.String(required=True)
    logo = Upload()


class CompanyListOutputType(graphene.ObjectType):
    total_count = graphene.Int()
    results = graphene.List(CompanyType)
