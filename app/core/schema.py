import graphene
import graphql_jwt
from user.query import Query as UserQuery
from user.mutations import Mutation as UserMutation
from user.subscriptions import UserSubscription
from company.query import Query as CompanyQuery
from company.mutations import Mutation as CompanyMutation


class Query(UserQuery, CompanyQuery, graphene.ObjectType):
    pass


class Mutation(UserMutation, CompanyMutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
