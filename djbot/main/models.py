from django.db import models


class Game(models.Model):
    gamename = models.TextField(
        verbose_name="Название игры",
    )

    def __str__(self):
        return f'{self.gamename}'

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"


class UserProfile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name="Внешний ID пользователя",
        unique=True,
    )
    name = models.TextField(
        null=True,
        verbose_name="Имя пользователя",
    )
    main_game = models.TextField(
        null=True,
        verbose_name="Основная игра",
    )
    steam_nickname = models.TextField(
        null=True,
        verbose_name="Никнейм в Steam",
    )
    about = models.TextField(
        null=True,
        verbose_name="О пользователе",
    )

    in_search = models.BooleanField(
        null=True,
        verbose_name="Статус в поиске",
    )

    def __str__(self):
        return f'#{self.external_id} {self.name}'

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class Message(models.Model):
    profile = models.ForeignKey(
        to='main.User_Profile',
        verbose_name="Профиль",
        on_delete=models.PROTECT,
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    created_at = models.DateTimeField(
        verbose_name="Время получения",
        auto_now_add=True,
    )

    def __str__(self):
        return f'Сообщение {self.pk} от {self.profile}'

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
