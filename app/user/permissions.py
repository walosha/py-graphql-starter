from rest_framework import permissions
from django_graphene_permissions.permissions import BasePermission
from .models import User


class IsAuthenticated(BasePermission):
    """Allows access only to admin users. """
    message = "You have to be logged in to perform this action"

    @staticmethod
    def has_permission(context):
        return context.user and context.user.is_authenticated


class IsSuperAdmin(BasePermission):
    """Allows access only to super admin users. """
    message = "Only Super Admins are authorized to perform this action."

    @staticmethod
    def has_permission(context):
        return bool(context.user and context.user.is_authenticated and context.user.roles
                    and 'SUPERADMIN' in context.user.roles)


class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users. """
    message = "Only Admins are authorized to perform this action."

    @staticmethod
    def has_permission(context):
        return bool(context.user and context.user.is_authenticated and context.user.roles
                    and 'ADMIN' in context.user.roles)


class IsStudentUser(permissions.BasePermission):
    """Allows access only to student users. """
    message = "Only students users are authorized to perform this action."

    @staticmethod
    def has_permission(context):
        return bool(context.user and context.user.is_authenticated and context.user.roles
                    and 'STUDENT' in context.user.roles)


class IsInstructorUser(permissions.BasePermission):
    """Allows access only to instructor users. """
    message = "Only instructors users are authorized to perform this action."

    @staticmethod
    def has_permission(context):
        return bool(context.user and context.user.is_authenticated and context.user.roles
                    and 'STUDENT' in context.user.roles)


class IsCompanyUserAndAdmin(BasePermission):
    """Allows access only to company user who is an admin. """
    message = "You have to be part of a company to perform this action"

    @staticmethod
    def has_permission(context):
        return bool(context.user.is_authenticated and context.user.company and 'ADMIN' in context.user.roles)
