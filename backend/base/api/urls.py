from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", views.CreateUser.as_view()),
    path("rooms/", views.RoomList.as_view()),
    path("room_reservations/", views.RoomReservationList.as_view()),
    path("room_reservations/<int:pk>/", views.RoomReservation.as_view()),
]
