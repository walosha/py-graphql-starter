import graphene
import graphql_jwt
from graphql import GraphQLError
from datetime import datetime
import graphql_social_auth
from graphql_jwt.shortcuts import get_token
from graphene_django_extras import DjangoSerializerMutation
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.conf import settings
from email_validator import validate_email, EmailNotValidError
from graphene_file_upload.scalars import Upload
from .types import (RegisterUserInputType,  RegisterUserOutputType, SignupRoleEnum, UserType, ResponseHandler, )
from .serializers import ListUserSerializer, CreateUserSerializer
from .tasks import send_password_reset_email, send_confirm_password_reset_email, send_verify_email
from .models import Token, User


class UserSerializerMutation(DjangoSerializerMutation):
    """
        DjangoSerializerMutation auto implement
        Create, Delete and Update functions
    """
    class Meta:
        description = " DRF serializer based Mutation for User "
        serializer_class = CreateUserSerializer


class VerifyEmailMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        role = SignupRoleEnum()

    ok = graphene.Boolean()
    success = graphene.Field(ResponseHandler)
    errors = graphene.Field(ResponseHandler)

    @staticmethod
    def mutate(root, info, email=None, role=None):
        try:
            valid = validate_email(email)
        except EmailNotValidError as e:
            errors = ResponseHandler(
                messages='invalid email address')
            return VerifyEmailMutation(errors=errors, ok=False)
        existing_user = get_user_model().objects.filter(
            email=valid.email.lower()).first()
        if existing_user:
            errors = ResponseHandler(
                messages='Email already exists, please login')
            return VerifyEmailMutation(errors=errors, ok=False)
        token = Token.objects.create(
            new_user_email=valid.email.lower().strip(), type='VERIFY_EMAIL', token=get_random_string(length=100))
        role = role.lower()
        frontend_url = settings.FRONTEND_URL
        email_data = {'email': valid.email.lower(), 'token': token.token,
                      'reset_password_url': f'{frontend_url}/signup/{role}?token={token.token}'}
        send_verify_email.delay(email_data)
        response = ResponseHandler(
            messages='A verification link has been sent to your email')
        return VerifyEmailMutation(success=response, ok=True)


def create_user(user_details, role):
    token = Token.objects.filter(token=user_details.email_verify_token).first()
    if not token:
        errors = ResponseHandler(messages='Token is invalid or expired')
        return errors, None
    user_details['email'] = token.new_user_email
    user_details.pop('email_verify_token', None)
    user = get_user_model().objects.create(**user_details, role=role)
    user.set_password(user_details['password'])
    user.save()
    token.delete()
    return None, user


def generate_user_output_type(user):
    return UserType(
        id=user.id,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        role=user.role,
        phone=user.phone,
        image=user.image
    )


class CreateUserMutation(graphene.Mutation):
    class Arguments:
        user_details = RegisterUserInputType(required=True)
    ok = graphene.Boolean()
    user = graphene.Field(RegisterUserOutputType)
    errors = graphene.Field(ResponseHandler)

    @staticmethod
    def mutate(root, info, user_details=None, **kwargs):
        errors, user = create_user(user_details)
        if errors:
            return CreateUserMutation(errors=errors, ok=False)
        user = RegisterUserOutputType(
            id=user.id,
            email=user.email,
            firstname=user.firstname,
            lastname=user.lastname,
            role=user.role,
            access_token=get_token(user),
        )
        return CreateUserMutation(user=user, ok=True)


class SocialAuthMutation(graphql_social_auth.SocialAuthMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, social, **kwargs):
        return cls(user=social.user)


class ForgetPasswordMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
    ok = graphene.Boolean()
    success = graphene.Field(ResponseHandler)
    errors = graphene.Field(ResponseHandler)

    @staticmethod
    def mutate(root, info, email=None):
        existing_user = get_user_model().objects.filter(email=email.lower()).first()
        if not existing_user:
            errors = ResponseHandler(messages='Email does not exist')
            return ForgetPasswordMutation(errors=errors, ok=False)
        token = Token.objects.create(
            user=existing_user, type='PASSWORD_RESET', token=get_random_string(length=100))
        email_data = {'firstname': existing_user.firstname, 'lastname': existing_user.lastname, 'email': existing_user.email,
                      'token': token.token, 'reset_password_url': f'{settings.FRONTEND_URL}/password/reset/{token.token}'}
        send_password_reset_email.delay(email_data)
        response = ResponseHandler(
            messages='Reset link has been sent to your email')
        return ForgetPasswordMutation(success=response, ok=True)


class ResetPasswordMutation(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        new_password = graphene.String(required=True)
    ok = graphene.Boolean()
    success = graphene.Field(ResponseHandler)
    errors = graphene.Field(ResponseHandler)

    @staticmethod
    def mutate(root, info, token=None, new_password=None):
        token_data = Token.objects.filter(token=token).first()
        if not token_data:
            errors = ResponseHandler(messages='Token is invalid or expired')
            return ResetPasswordMutation(errors=errors, ok=False)
        if token_data and not token_data.is_valid:
            errors = ResponseHandler(messages='Token is invalid or expired')
            return ResetPasswordMutation(errors=errors, ok=False)
        token_data.user.set_password(new_password)
        token_data.user.save()
        token_data.delete()
        email_data = {'firstname': token_data.user.firstname, 'lastname': token_data.user.lastname,
                      'email': token_data.user.email}
        send_confirm_password_reset_email.delay(email_data)
        response = ResponseHandler(
            messages='Password has been changed successfully')
        return ResetPasswordMutation(success=response, ok=True)


class LoginMutation(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)
    ok = graphene.Boolean()

    @classmethod
    def resolve(cls, root, info, **kwargs):
        user = info.context.user
        user.last_login = datetime.now()
        user.save()
        return cls(user=user,  ok=True)


class Mutation(graphene.ObjectType):
    # create_user = CreateUserMutation.Field()
    verify_user_email = VerifyEmailMutation.Field()
    create_user = UserSerializerMutation.CreateField()
    update_user = UserSerializerMutation.UpdateField()
    delete_user = UserSerializerMutation.DeleteField()
    forgot_password = ForgetPasswordMutation.Field()
    reset_password = ResetPasswordMutation.Field()
    social_auth = graphql_social_auth.SocialAuthJWT.Field()
    login = LoginMutation.Field()
