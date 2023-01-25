import graphene
from django.db.models import Q
from graphql import GraphQLError
from graphene_django_extras import DjangoObjectField, DjangoListObjectField
from django_graphene_permissions import permissions_checker

from company.models import Company
from helpers import paginate_queryset
from .models import User, Token
from .permissions import IsAuthenticated, IsSuperAdmin
from .types import UserType, UserListType, VerifyTokenOutputType, UserListOutputType


class Query(graphene.ObjectType):
    logged_in_user = graphene.Field(UserType, description='Get details of the logged in user')
    all_users = graphene.Field(UserListOutputType, search=graphene.String(), offset=graphene.Int(),
                               limit=graphene.Int(), ordering=graphene.String(),
                               description='Get list of registered users')
    users_by_company = graphene.Field(UserListOutputType, company_id=graphene.UUID(), search=graphene.String(),
                                      offset=graphene.Int(), limit=graphene.Int(), ordering=graphene.String(),
                                      description='Get list of registered users in a given companies')
    users = graphene.Field(UserListOutputType, company_id=graphene.UUID(), search=graphene.String(),
                           offset=graphene.Int(), limit=graphene.Int(), ordering=graphene.String(),
                           description='Get list of all registered users in the my company')
    user_list = DjangoListObjectField(
        UserListType, description="User List Query")
    verify_register_token = graphene.Field(
        VerifyTokenOutputType, token=graphene.String(required=True))

    @permissions_checker([IsAuthenticated, IsSuperAdmin])
    def resolve_all_users(self, info, search=None, offset=None, limit=None, ordering=None):
        qs = User.objects.all()
        if search:
            custom_filter = (
                    Q(firstname__icontains=search) |
                    Q(lastname__icontains=search)
            )
            qs = qs.filter(custom_filter)
        return paginate_queryset(qs, offset, limit, ordering)

    @permissions_checker([IsAuthenticated])
    def resolve_users(self, info, search=None, offset=None, limit=None, ordering=None):
        company = info.context.user.company
        if company is None:
            raise GraphQLError('User does not belong to any company')
        qs = User.objects.filter(company=company)
        if search:
            custom_filter = (
                    Q(firstname__icontains=search) |
                    Q(lastname__icontains=search)
            )
            qs = qs.filter(custom_filter)
        return paginate_queryset(qs, offset, limit, ordering)

    @permissions_checker([IsAuthenticated])
    def resolve_logged_in_user(self, info):
        return info.context.user

    @permissions_checker([IsAuthenticated])
    def resolve_users_by_company(self, info, company_id, search=None, offset=None, limit=None, ordering=None):
        company = Company.objects.filter(id=company_id).first()
        if company is None:
            raise GraphQLError('Invalid company id specified')
        qs = User.objects.filter(company=company)
        if search:
            custom_filter = (
                    Q(firstname__icontains=search) |
                    Q(lastname__icontains=search)
            )
            qs = qs.filter(custom_filter)
        return paginate_queryset(qs, offset, limit, ordering)

    def resolve_verify_register_token(self, info, token=None):
        if token is not None:
            user_token = Token.objects.filter(token=token).first()
            if user_token:
                return {
                    'email': user_token.new_user_email is None and user_token.user or user_token.new_user_email,
                    'is_valid': True
                }
            return {'email': None, 'is_valid': False}
        raise GraphQLError('invalid token')



