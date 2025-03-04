# Generated by Django 5.1.6 on 2025-03-01 13:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tables', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата бронирования')),
                ('time', models.TimeField(verbose_name='Время бронирования')),
                ('duration', models.PositiveIntegerField(verbose_name='Длительность (минуты)')),
                ('status', models.CharField(choices=[('pending', 'Ожидает подтверждения'), ('confirmed', 'Подтверждено'), ('cancelled', 'Отменено')], default='pending', max_length=20, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tables.table', verbose_name='Столик')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
