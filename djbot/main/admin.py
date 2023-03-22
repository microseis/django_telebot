from django.contrib import admin

from main.forms import ProfileForm
from main.models import Game, Message, UserProfile


@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "external_id",
        "name",
        "main_game",
        "steam_nickname",
        "about",
        "in_search",
    )
    form = ProfileForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "text", "created_at")


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "gamename")
