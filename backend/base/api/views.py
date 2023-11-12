from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from .permissions import IsObjectUser
from .. import models
from . import serializers, utils
from datetime import date as dt_date, datetime as dt_datetime
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter


@extend_schema_view(post=extend_schema(summary="Create new User"))
class CreateUser(CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.CreateUserSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Get Room List",
        parameters=[
            OpenApiParameter(
                name="begin",
                location=OpenApiParameter.QUERY,
                description="Begin date of desired Room Reservation, will filter out any Rooms, whose reservations are overlapping",
                required=False,
                type=dt_date,
            ),
            OpenApiParameter(
                name="end",
                location=OpenApiParameter.QUERY,
                description="End date of desired Room Reservation, will filter out any Rooms, whose reservations are overlapping",
                required=False,
                type=dt_date,
            ),
        ],
    )
)
class RoomList(ListAPIView):
    serializer_class = serializers.RoomSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = (
        "price",
        "capacity",
    )
    filterset_fields = {
        "price": ("gte", "lte", "gt", "lt", "exact"),
        "capacity": ("gte", "lte", "gt", "lt", "exact"),
    }

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Custom filtering in queryset to not break the default filtering
    def get_queryset(self):
        queryset = models.Room.objects.all()

        from_date = utils.validate_queryparam_date(self.request, "begin")
        until_date = utils.validate_queryparam_date(self.request, "end")

        if from_date or until_date:
            overlapped_reservations = models.RoomReservation.get_reservations_in_range(
                from_date, until_date, status=models.RoomReservation.Status.ORDERED
            )

            queryset = queryset.exclude(
                number__in=overlapped_reservations.values_list(
                    "room__number", flat=True
                ).distinct()
            )

        return queryset


@extend_schema_view(
    get=extend_schema(summary="Get Current User Room Reservations"),
    post=extend_schema(summary="Create new Room Reservation"),
)
class RoomReservationList(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.RoomReservationSerializer
    filter_backends = (OrderingFilter,)
    ordering = ("-date_begin", "-date_end")

    def get_queryset(self):
        user: models.User = self.request.user
        return user.roomreservation_set.all()


@extend_schema_view(
    get=extend_schema(summary="Get Room Reservation"),
    delete=extend_schema(summary="Cancel Room Reservation"),
)
class RoomReservation(RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated, IsObjectUser)
    serializer_class = serializers.RoomReservationSerializer

    def get_queryset(self):
        user: models.User = self.request.user
        return user.roomreservation_set.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance: models.RoomReservation) -> None:
        instance.status = instance.Status.CANCELLED
        instance.save()
