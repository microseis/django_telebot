from django import forms

from .models import User_Profile, Game


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User_Profile
        fields =(
            'external_id', "name", 'main_game', 'steam_nickname', 'about'
        )
        widgets = {'name': forms.TextInput,
                   'main_game': forms.TextInput,
                   'steam_nickname': forms.TextInput,
                   'about': forms.TextInput,}


class GameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields =(
            "gamename",
        )
        widgets = {'gamename': forms.TextInput,}