from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import datetime, timedelta
from .models import Reservation
from .tasks import send_reservation_confirmation_email_task, auto_cancel_unconfirmed_reservation


@receiver(post_save, sender=Reservation)
def schedule_reservation_tasks(sender, instance, created, **kwargs):
    """Планирует отправку email и автоотмену брони"""
    if not created:
        return

    reservation_datetime = datetime.combine(instance.date, instance.time)

    """ Запускаем email-уведомление за 1 час"""
    email_send_time = reservation_datetime - timedelta(minutes=60)
    email_countdown = (email_send_time - now()).total_seconds()
    if email_countdown > 0:
        send_reservation_confirmation_email_task.apply_async(args=[instance.id], countdown=email_countdown)

    """ Запускаем автоотмену за 15 минут"""
    cancel_time = reservation_datetime - timedelta(minutes=15)
    cancel_countdown = (cancel_time - now()).total_seconds()
    if cancel_countdown > 0:
        auto_cancel_unconfirmed_reservation.apply_async(args=[instance.id], countdown=cancel_countdown)
