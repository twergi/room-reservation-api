from rest_framework.serializers import (
    ModelSerializer,
    CurrentUserDefault,
    HiddenField,
    SerializerMethodField,
)
from .. import models
from .serializer_mixins import ValidateModelMixin
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class CreateUserSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            "username",
            "email",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: dict) -> models.User:
        return self.Meta.model.objects.create_user(**validated_data)


class RoomSerializer(ModelSerializer):
    class Meta:
        model = models.Room
        fields = (
            "number",
            "price",
            "capacity",
        )


class RoomReservationSerializer(ValidateModelMixin, ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())
    # status = ReadOnlyField(source="get_status_display")
    status = SerializerMethodField()

    class Meta:
        model = models.RoomReservation
        fields = (
            "id",
            "room",
            "user",
            "date_begin",
            "date_end",
            "full_price",
            "status",
        )

        extra_kwargs = {
            "id": {"read_only": True},
            "full_price": {"read_only": True},
        }

    def create(self, validated_data):
        return self.Meta.model.create(**validated_data)

    @extend_schema_field(OpenApiTypes.STR)
    def get_status(self, object: models.RoomReservation):
        return object.get_status_display()
