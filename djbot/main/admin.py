from django.contrib import admin

from .models import User_Profile, Game, Message
from .forms import ProfileForm


@admin.register(User_Profile)
class ProfileAdmin (admin.ModelAdmin):
    list_display = ('id', "external_id", "name", 'main_game', 'steam_nickname', 'about', 'in_search')
    form = ProfileForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'text', 'created_at')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'gamename')

