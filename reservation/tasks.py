import logging
from celery import shared_task
from django.utils.timezone import now
from .models import Reservation
from utils import send_booking_confirmation_email

logger = logging.getLogger(__name__)

@shared_task
def send_reservation_confirmation_email_task(reservation_id):
    """Celery-задача для отправки email перед бронированием"""
    try:
        reservation = Reservation.objects.select_related("user", "table").get(id=reservation_id)
        if reservation.status in ["pending", "confirmed"]:
            send_booking_confirmation_email(
                reservation.user.email, reservation.id, reservation.table.id, reservation.date, reservation.time
            )
    except Reservation.DoesNotExist:
        logger.warning(f"Бронирование {reservation_id} не найдено для отправки email.")
    except Exception as e:
        logger.error(f"Ошибка при отправке email для бронирования {reservation_id}: {e}")

@shared_task
def auto_cancel_unconfirmed_reservation(reservation_id):
    """Отменяет бронирование, если оно не подтверждено за 15 минут до начала"""
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        if reservation.status == "pending":
            reservation.status = "cancelled"
            reservation.save()
            logger.info(f"Бронирование {reservation_id} автоматически отменено.")
    except Reservation.DoesNotExist:
        logger.warning(f"Бронирование {reservation_id} не найдено для автоотмены.")
    except Exception as e:
        logger.error(f"Ошибка при автоотмене бронирования {reservation_id}: {e}")
