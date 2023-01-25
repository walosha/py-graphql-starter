import graphene
from django.db.models import Q
from graphql import GraphQLError
from graphene_django_extras import DjangoObjectField, DjangoListObjectField
from django_graphene_permissions import permissions_checker

from helpers import paginate_queryset
from user.permissions import IsAuthenticated
from .models import Company
from .types import CompanyType, CompanyInputType, CompanyListType, CompanyListOutputType


class Query(graphene.ObjectType):
    companies = graphene.Field(CompanyListOutputType, search=graphene.String(),  offset=graphene.Int(),
                               limit=graphene.Int(), ordering=graphene.String(),
                               description='Get list of registered companies')
    # company_list = graphene.List(CompanyListType, description='Get list of registered companies')
    company = graphene.Field(CompanyType, id=graphene.UUID())

    def resolve_companies(self, info, search=None, offset=None, limit=None, ordering=None):
        qs = Company.objects.all()
        if search:
            custom_filter = (
                    Q(name__icontains=search) |
                    Q(address__icontains=search)
            )
            qs = qs.filter(custom_filter)
        return paginate_queryset(qs, offset, limit, ordering)

    def resolve_company(self, info, id):
        return Company.objects.filter(pk=id).first()

