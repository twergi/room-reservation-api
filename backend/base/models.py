from django.db import models
from django.contrib.auth.models import User
from datetime import date as dt_date, timedelta as dt_timedelta
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from typing import Optional
from django.conf import settings


class Room(models.Model):
    number: int = models.PositiveIntegerField(
        primary_key=True,
        verbose_name="Room number",
    )
    price: float = models.FloatField(verbose_name="Cost per day")
    capacity: int = models.PositiveIntegerField(verbose_name="Room capacity")

    class Meta:
        verbose_name: str = "Room"
        verbose_name_plural: str = "Rooms"

    def clean(self) -> None:
        if self.price < 0.0:
            raise ValidationError("Price cannot be negative")

    def __str__(self) -> str:
        return f"Room #{self.number}, Price: {self.price}, Capacity: {self.capacity}"


class RoomReservation(models.Model):
    class Status(models.TextChoices):
        ORDERED = "ORDERED", "Ordered"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id: int = models.BigAutoField(primary_key=True, verbose_name="Id")
    room: Room = models.ForeignKey(
        to=Room, on_delete=models.RESTRICT, verbose_name="Room"
    )
    user: User = models.ForeignKey(to=User, on_delete=models.RESTRICT)
    date_begin: dt_date = models.DateField(verbose_name="From Date", db_index=True)
    date_end: dt_date = models.DateField(verbose_name="Until Date", db_index=True)
    full_price: float = models.FloatField(
        verbose_name="Price", validators=(MinValueValidator(0.0),)
    )
    status: str = models.CharField(
        verbose_name="Status",
        max_length=32,
        choices=Status.choices,
        default=Status.ORDERED,
    )

    class Meta:
        verbose_name: str = "Room Reservation"
        verbose_name_plural: str = "Room Reservations"

    @classmethod
    def create(cls, **kwargs):
        room_reservation = cls(**kwargs)
        room_reservation.full_price = room_reservation.calculate_full_price()
        room_reservation.save()
        return room_reservation

    @classmethod
    def get_reservations_in_range(
        cls, date_begin: Optional[dt_date], date_end: Optional[dt_date], status: str
    ) -> models.QuerySet:
        """
        Returns `QuerySet` with all `RoomReservation`'s with provided `status`.
        At least one from `date_begin` or `date_end` must be specified.
        `status` must be
        """
        assert date_begin or date_end, "At least one argument must be specified"

        # Because Q __range is inclusive, we should make delta by one day
        day_delta = dt_timedelta(days=1)

        if date_begin and date_end:
            q = (
                models.Q(date_begin__range=(date_begin, date_end - day_delta))
                | models.Q(date_end__range=(date_begin + day_delta, date_end))
                | models.Q(date_begin__lt=date_begin, date_end__gt=date_end)
            )

        elif date_begin:
            q = models.Q(date_begin__gte=date_begin) | models.Q(date_end__gt=date_begin)

        elif date_end:
            q = models.Q(date_begin__lt=date_end) | models.Q(date_end__lte=date_end)

        q.add(models.Q(status=status), models.Q.AND)

        return cls.objects.filter(q)

    def calculate_full_price(self) -> float:
        """
        Calculates `full_price` of reservation, based on `room.price`, `date_begin` and `date_end`
        """
        return self.room.price * (self.date_end - self.date_begin).days

    def check_overlaps(self) -> None:
        """
        Checks if `room` with the same `number` is reserved on provided days
        """
        overlapped_reservations = RoomReservation.get_reservations_in_range(
            self.date_begin, self.date_end, status=self.Status.ORDERED
        )

        # Checking room reservations only with the same room number
        overlapped_reservations = overlapped_reservations.filter(
            room__number=self.room.number
        )

        # When updating existing room reservations, we should exclude it
        if self.id:
            overlapped_reservations = overlapped_reservations.exclude(id=self.id)

        if overlapped_reservations:
            msg = "Room Reservation with the same Room number already exists in date range"
            raise ValidationError(
                {
                    "date_begin": _(msg),
                    "date_end": _(msg),
                }
            )

    def check_dates(self) -> None:
        """
        Checks if `date_end` is later, than `date_begin`
        """
        if self.date_begin >= self.date_end:
            msg = "End date must be later, than begin date"
            raise ValidationError(
                {
                    "date_begin": _(msg),
                    "date_end": _(msg),
                }
            )

    def clean(self) -> None:
        self.check_dates()
        self.check_overlaps()

    def __str__(self) -> str:
        return f"Room Reservation of Room #{self.room.number} from {self.date_begin.strftime(settings.DATE_FORMAT)} until {self.date_end.strftime(settings.DATE_FORMAT)}"
