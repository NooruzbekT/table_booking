from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings


def send_booking_confirmation_email(user_email, reservation_id, table_id, date, time):
    """Отправляет email со ссылкой на подтверждение бронирования"""

    confirm_url = f"http://127.0.0.1:8000/api/reservation/confirm-reservation/{reservation_id}/"

    formatted_date = date.strftime("%d.%m.%Y")
    formatted_time = time.strftime("%H:%M")

    subject = "Подтверждение бронирования"
    message = (
        f"Вы забронировали столик №{table_id} на {formatted_date} в {formatted_time}.\n\n"
        f"Подтвердите бронирование по ссылке: {confirm_url}\n\n"
        "Если вы не подтвердите его за 15 минут до начала, бронь будет автоматически отменена."
    )

    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email], fail_silently=True)
