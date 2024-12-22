from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from main.models import Game

markup = InlineKeyboardMarkup()
markup_search = InlineKeyboardMarkup()
markup_visibility = InlineKeyboardMarkup()

all_games = Game.objects.all()

if not all_games:
    inline_btn = InlineKeyboardButton(
        "Игры не заданы администратором", callback_data="games_not_set"
    )
    markup.insert(inline_btn)
else:
    for game in all_games:
        inline_btn = InlineKeyboardButton(game.gamename, callback_data=game.gamename)
        markup.insert(inline_btn)

inline_btn_ok = InlineKeyboardButton(
    "✅ Выбрать пользователя", callback_data="user_selected"
)
inline_btn_next = InlineKeyboardButton(
    "❌ Другой пользователь", callback_data="next_user"
)

markup_search.add(inline_btn_next, inline_btn_ok)


inline_btn_vis = InlineKeyboardButton("Доступен для поиска", callback_data="visible")
inline_btn_visibility = InlineKeyboardButton("Скрыт", callback_data="invisible")

markup_visibility.add(inline_btn_vis, inline_btn_visibility)
