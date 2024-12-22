from django.db import models


class Game(models.Model):
    """Игра."""
    gamename = models.TextField(
        verbose_name="Название игры", unique=True, null=False
    )

    def __str__(self) -> str:
        return f"{self.gamename}"

    class Meta:
        verbose_name: str = "Игра"
        verbose_name_plural: str = "Игры"


class UserProfile(models.Model):
    """Профиль пользователя."""
    external_id = models.PositiveIntegerField(
        verbose_name="Внешний ID пользователя", unique=True,
    )
    name = models.TextField(null=False, verbose_name="Имя пользователя")
    main_game = models.TextField(null=False, verbose_name="Основная игра")
    steam_nickname = models.TextField(null=False, verbose_name="Никнейм в Steam")
    about = models.TextField(null=True, verbose_name="О пользователе")
    in_search = models.BooleanField(null=True, verbose_name="Статус в поиске")

    def __str__(self) -> str:
        return f"#{self.external_id} {self.name}"

    class Meta:
        verbose_name: str = "Профиль"
        verbose_name_plural: str = "Профили"


class Message(models.Model):
    """Сообщение пользователя."""
    profile = models.ForeignKey(
        to="main.UserProfile", verbose_name="Профиль", on_delete=models.PROTECT)
    text = models.TextField(verbose_name="Текст", null=False)
    created_at = models.DateTimeField(verbose_name="Время получения", auto_now_add=True)

    def __str__(self) -> str:
        return f"Сообщение {self.pk} от {self.profile}"

    class Meta:
        verbose_name: str = "Сообщение"
        verbose_name_plural: str = "Сообщения"
