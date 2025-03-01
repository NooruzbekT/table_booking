from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from .models import Reservation
from .serializers import ReservationSerializer
from .utils import send_booking_confirmation_email  # Assuming this is your utility function

from rest_framework.exceptions import AuthenticationFailed


class ReservationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Создание бронирования с проверкой доступности столика"""
        if not request.user.is_authenticated:
            raise AuthenticationFailed("Пользователь не аутентифицирован")

        # Передача контекста в сериализатор
        serializer = ReservationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            table = serializer.validated_data["table"]
            date = serializer.validated_data["date"]
            time = serializer.validated_data["time"]
            duration = serializer.validated_data["duration"]

            start_datetime = datetime.combine(date, time)
            end_datetime = start_datetime + timedelta(minutes=duration)

            # Проверка пересечения бронирований
            existing_reservations = Reservation.objects.filter(
                table=table,
                date=date,
                status__in=["pending", "confirmed"]
            ).filter(
                time__lt=end_datetime.time(),
                time__gte=start_datetime.time()
            )

            if existing_reservations.exists():
                return Response(
                    {"error": "Этот столик уже забронирован в указанное время."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Проверка ограничения на 3 бронирования
            active_reservations = Reservation.objects.filter(
                user=request.user,
                status__in=["pending", "confirmed"]
            ).count()

            if active_reservations >= 3:
                return Response(
                    {"error": "Вы не можете иметь больше 3 активных бронирований."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            reservation = serializer.save(user=request.user, status="pending")

            send_booking_confirmation_email(
                user_email=request.user.email,
                reservation_id=reservation.id,
                table_id=table.id,
                date=date,
                time=time
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationUpdateDestroyView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """Изменение времени бронирования (если столик свободен)"""
        try:
            reservation = Reservation.objects.get(id=kwargs['pk'])
        except Reservation.DoesNotExist:
            return Response(
                {"error": "Бронирование не найдено."},
                status=status.HTTP_404_NOT_FOUND
            )

        if reservation.status != "pending":
            return Response(
                {"error": "Можно изменить только ожидающее подтверждения бронирование."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReservationSerializer(reservation, data=request.data, partial=True)
        if serializer.is_valid():
            new_date = serializer.validated_data.get("date", reservation.date)
            new_time = serializer.validated_data.get("time", reservation.time)
            new_duration = serializer.validated_data.get("duration", reservation.duration)

            new_start_datetime = datetime.combine(new_date, new_time)
            new_end_datetime = new_start_datetime + timedelta(minutes=new_duration)

            overlapping_reservations = Reservation.objects.filter(
                table=reservation.table,
                date=new_date,
                status__in=["pending", "confirmed"]
            ).filter(
                time__lt=new_end_datetime.time(),
                time__gte=new_start_datetime.time()
            ).exclude(id=reservation.id)

            if overlapping_reservations.exists():
                return Response(
                    {"error": "Этот столик уже забронирован на новое время."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Отмена бронирования (не позднее чем за 30 минут до начала)"""
        try:
            reservation = Reservation.objects.get(id=kwargs['pk'])
        except Reservation.DoesNotExist:
            return Response(
                {"error": "Бронирование не найдено."},
                status=status.HTTP_404_NOT_FOUND
            )

        if reservation.status == "cancelled":
            return Response(
                {"error": "Бронирование уже отменено."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_time = datetime.combine(reservation.date, reservation.time)
        if datetime.now() + timedelta(minutes=30) >= start_time:
            return Response(
                {"error": "Нельзя отменить бронирование менее чем за 30 минут до начала."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = "cancelled"
        reservation.save()
        return Response({"message": "Бронирование отменено."}, status=status.HTTP_200_OK)


class ConfirmReservationView(APIView):

    def get(self, request, pk=None):
        """Подтверждение бронирования через URL"""
        reservation = get_object_or_404(Reservation, id=pk, status="pending")
        reservation.status = "confirmed"
        reservation.save()
        return Response({"message": "Бронирование подтверждено."}, status=status.HTTP_200_OK)
