from datetime import datetime, timedelta
from rest_framework import serializers
from .models import Reservation
from tables.models import Table


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "user", "table", "date", "time", "duration", "status", "created_at"]
        read_only_fields = ["status", "created_at", "user"]  # Поля, которые нельзя изменять напрямую

    def validate(self, data):
        """ Проверка доступности столика на указанное время. """
        request = self.context.get("request")

        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Требуется авторизация.")

        user = request.user
        table = data.get("table", getattr(self.instance, "table", None))
        date = data.get("date", getattr(self.instance, "date", None))
        time = data.get("time", getattr(self.instance, "time", None))
        duration = data.get("duration", getattr(self.instance, "duration", None))

        if table and date and time and duration:
            start_datetime = datetime.combine(date, time)
            end_datetime = start_datetime + timedelta(minutes=duration)

            # Проверяем пересечения бронирований
            overlapping_reservations = Reservation.objects.filter(
                table=table,
                date=date,
                status__in=["pending", "confirmed"]
            ).exclude(id=self.instance.id if self.instance else None).filter(
                time__lt=end_datetime.time(),
                time__gte=start_datetime.time()
            ).exists()

            if overlapping_reservations:
                raise serializers.ValidationError("Этот столик уже забронирован на указанное время.")


        if self.instance is None:
            active_reservations = Reservation.objects.filter(
                user=user, status__in=["pending", "confirmed"]
            ).count()
            if active_reservations >= 3:
                raise serializers.ValidationError("У вас уже есть 3 активных бронирования.")

        data["user"] = user
        return data
