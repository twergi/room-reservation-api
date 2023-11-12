from rest_framework.permissions import BasePermission
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.db.models import Model
    from rest_framework.views import APIView


class IsObjectUser(BasePermission):
    def has_object_permission(
        self, request: "HttpRequest", view: "APIView", obj: "Model"
    ):
        assert hasattr(obj, "user"), 'Object doesn\'t have "user" attribute'
        return obj.user == request.user
