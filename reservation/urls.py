from django.urls import path
from .views import ConfirmReservationView, ReservationUpdateDestroyView,ReservationCreateView

urlpatterns = [
    path('create/', ReservationCreateView.as_view(), name='reservation-create'),  # Для создания бронирования
    path('reservations/<int:pk>/', ReservationUpdateDestroyView.as_view(), name='reservation-detail'),  # Для получения/обновления/удаления бронирования
    path('confirm-reservation/<int:pk>/', ConfirmReservationView.as_view(), name='confirm_reservation'),
    # Для подтверждения бронирования
]
