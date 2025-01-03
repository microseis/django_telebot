# Generated by Django 5.1.4 on 2024-12-21 10:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("gamename", models.TextField(verbose_name="Название игры")),
            ],
            options={
                "verbose_name": "Игра",
                "verbose_name_plural": "Игры",
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "external_id",
                    models.PositiveIntegerField(
                        unique=True, verbose_name="Внешний ID пользователя"
                    ),
                ),
                ("name", models.TextField(null=True, verbose_name="Имя пользователя")),
                (
                    "main_game",
                    models.TextField(null=True, verbose_name="Основная игра"),
                ),
                (
                    "steam_nickname",
                    models.TextField(null=True, verbose_name="Никнейм в Steam"),
                ),
                ("about", models.TextField(null=True, verbose_name="О пользователе")),
                (
                    "in_search",
                    models.BooleanField(null=True, verbose_name="Статус в поиске"),
                ),
            ],
            options={
                "verbose_name": "Профиль",
                "verbose_name_plural": "Профили",
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(verbose_name="Текст")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Время получения"
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="main.userprofile",
                        verbose_name="Профиль",
                    ),
                ),
            ],
            options={
                "verbose_name": "Сообщение",
                "verbose_name_plural": "Сообщения",
            },
        ),
    ]
