import graphene
from graphene_django_extras import DjangoSerializerMutation
from .models import Company
from .serializers import CompanySerializer
from .types import CompanyType, CompanyInputType, CompanyListType


class CompanySerializerMutation(DjangoSerializerMutation):
    """
        DjangoSerializerMutation auto implement
        Create, Delete and Update functions
    """
    class Meta:
        description = " DRF serializer based Mutation for Company "
        serializer_class = CompanySerializer


class Mutation(graphene.ObjectType):
    create_company = CompanySerializerMutation.CreateField()
    update_company = CompanySerializerMutation.UpdateField()
    delete_company = CompanySerializerMutation.DeleteField()
