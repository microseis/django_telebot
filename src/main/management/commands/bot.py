
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from channels.db import database_sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from utils.logger import logger

from .keyboards import markup, markup_search, markup_visibility
from main.models import Game, UserProfile


storage = MemoryStorage()

all_games = Game.objects.all()
game_list: list = []

for game in all_games:
    game_list.append(game.gamename)

logger.info(f"available games: {game_list}")


class Form(StatesGroup):
    main_game = State()
    about = State()
    steam_nickname = State()


class FormSearch(StatesGroup):
    choose_game = State()
    choose_player = State()
    user_id = State()


class Command(BaseCommand):
    help = "Telegram Bot"

    def handle(self, *args, **options) -> None:
        """Bot logic."""
        bot = Bot(token=settings.TOKEN)
        dp = Dispatcher(bot=bot, storage=storage)

        @dp.message_handler(state="*", commands=["cancel"])
        @dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
        async def cancel_handler(message: Message, state: FSMContext) -> None:
            """Allow user to cancel any action."""

            current_state: str | None = await state.get_state()
            if current_state is None:
                return

            logger.info(f"Cancelling state {current_state}")

            await state.finish()

            await message.answer("Ваш запрос успешно отменен.")

        @dp.callback_query_handler(text="visible")
        async def process_callback_button1(message: Message) -> None:

            await update_visibility(message, vis=True)

            await message.answer("Ваш профиль теперь доступен для поиска")

        @dp.callback_query_handler(text="invisible")
        async def process_callback_button2(message: Message) -> None:

            await update_visibility(message, vis=False)

            await message.answer("Ваш профиль больше не доступен для поиска")

        @dp.message_handler(commands=["visibility"])
        async def process_about(message: Message) -> None:

            await message.answer(
                "Какую настройку видимости применить к вашему профилю?",
                reply_markup=markup_visibility,
            )

        @database_sync_to_async
        def get_user_data(data, message: Message) -> None:
            """Сохранение данных о пользователе в бд."""

            p, _ = UserProfile.objects.get_or_create(
                external_id=message.from_user.id,
                defaults={
                    "name": message.from_user.username,
                },
            )
            p.steam_nickname = data["steam_nickname"]
            p.main_game = data["main_game"]
            p.about = data["about"]
            p.in_search = True
            p.save()

        @database_sync_to_async
        def update_game(data, message: Message) -> None:
            p, _ = UserProfile.objects.get_or_create(
                external_id=message.from_user.id,
                defaults={
                    "name": message.from_user.username,
                },
            )
            p.main_game = data["choose_game"]
            p.save()

        @dp.message_handler(commands=["start"])
        async def send_welcome(message: Message) -> None:

            if not message.from_user.username:
                await message.answer(
                    "Пожалуйста установите Имя пользователя в настройках Telegram "
                    "для начала пользования ботом. Спасибо за понимание!"
                )

            if await user_exists(message):
                await message.answer(
                    f"Рады приветствовать вас снова, {message.from_user.first_name}! \n\n"
                    f"Для получения списка доступных команд нажмите  /help\n"
                    f"Для выбора игры и поиска случайного соперника нажмите /play\n\n"
                )
            else:
                await message.answer(
                    f"Добрый день, {message.from_user.first_name} {message.from_user.last_name}! \n\n"
                    f"Для того, чтобы начать пользоваться ботом, пожалуйста "
                    f"заполните данные о себе, нажав команду /profile"
                )

        @dp.message_handler(commands=["help"])
        async def allowed_commands(message: Message) -> None:
            """Список доступных команд бота."""
            if not message.from_user.username:
                await message.answer(
                    "Пожалуйста установите Имя пользователя в настройках Telegram "
                    "для начала пользования ботом. Спасибо за понимание!"
                )
            await message.answer(
                "Список доступных команд:\n\n"
                "/start - Начало работы с ботом\n"
                "/update - Редактирование данных профиля\n"
                "/play - Выбор игры и соперника\n"
                "/visibility - Изменение настроек видимости профиля\n"
                "/cancel - Отмена выполнения запроса\n\n"
            )

        @dp.message_handler(commands=["update", "profile"])
        async def send_update(message: Message) -> None:
            if not message.from_user.username:
                await message.answer(
                    "Пожалуйста установите Имя пользователя в настройках Telegram "
                    "для начала пользования ботом. Спасибо за понимание!"
                )
            await message.reply("Пожалуйста, введите данные о себе:")
            await Form.about.set()

        @dp.message_handler(state=Form.about)
        async def process_about_final(message: Message, state: FSMContext) -> None:
            if not len(message.text) > 2:
                await message.answer(
                    "А вы не так многословны :). Пожалуйста напишите о себе чуть-подробнее:"
                )
            async with state.proxy() as data:
                data["about"] = message.text

            await Form.main_game.set()
            await message.answer(
                "Отлично! В какую игру вы собираетесь поиграть?",
                reply_markup=markup,
            )

        @dp.callback_query_handler(lambda call: True, state=Form.main_game)
        async def process_game(call: types.CallbackQuery, state: FSMContext) -> None:
            async with state.proxy() as data:
                data["main_game"] = call.data
            try:
                await bot.edit_message_text(
                    text="Введите ваш никнейм в Steam:",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                )
                await Form.steam_nickname.set()
            except Exception as e:
                logger.debug(e)

        @dp.message_handler(state=Form.steam_nickname)
        async def process_steam(message: Message, state: FSMContext) -> None:
            async with state.proxy() as data:
                data["steam_nickname"] = message.text

            await get_user_data(data, message)
            await message.answer(
                f"Спасибо, вы успешно ввели следующие данные:\n\n"
                f"Инфо о себе: {data['about']}\n"
                f"Основная игра: {data['main_game']}\n"
                f"Никнейм в Steam: {data['steam_nickname']}\n\n"
                f"Для поиска игры и соперника нажмите /play"
            )
            await state.finish()

        @dp.message_handler(commands=["play"])
        async def process_play(message: Message) -> None:
            if message.from_user.username:
                await FormSearch.choose_game.set()
                await message.answer("В какую игру будем играть?", reply_markup=markup)
            else:
                await message.answer(
                    "Пожалуйста установите Имя пользователя в настройках Telegram для начала пользования ботом. "
                    "Спасибо за понимание!"
                )

        @dp.callback_query_handler(lambda call: True, state=FormSearch.choose_game)
        async def process_choose_game(call: types.CallbackQuery, state: FSMContext) -> None:
            async with state.proxy() as data:
                data["choose_game"] = call.data
            try:
                await bot.edit_message_text(
                    text=f"Вы выбрали игру: {call.data}\n\n"
                    f"Для поиска соперника нажми /search",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                )
                await update_game(data, call)
                await FormSearch.choose_player.set()
            except Exception as e:
                logger.debug(e)

        @dp.message_handler(commands=["search"], state=FormSearch.choose_player)
        async def process_search(message: Message, state: FSMContext) -> None:
            if message.from_user.username:
                async with state.proxy() as data:
                    data["user_id"] = message.from_user.id
                chosen_user: UserProfile = await get_random(data)
                if chosen_user is not None:
                    async with state.proxy() as data:
                        data["choose_player"] = chosen_user.external_id
                    await message.answer(
                        "Мы подобрали вам пользователя:\n"
                        f"Имя пользователя: @{chosen_user.name}\n"
                        f"Инфо: {chosen_user.about}\n"
                        f"Никнейм в Steam: {chosen_user.steam_nickname}\n\n"
                        "Нажми <Выбрать пользователя> если понравилась его карточка "
                        "для отправки ему сообщения или продолжите поиск\n"
                        "Для выхода из поиска или изменения настроек нажмите /cancel",
                        reply_markup=markup_search,
                    )

                else:
                    await message.answer(
                        "Для этой игры пока что нет подходящих соперников.\n\n"
                        "Попробуй выбрать другую игру",
                        reply_markup=markup,
                    )
                    await FormSearch.choose_game.set()

            else:
                await message.answer(
                    "Пожалуйста установите Имя пользователя в настройках Telegram "
                    "для начала пользования ботом. Спасибо за понимание!"
                )

        @dp.callback_query_handler(text="user_selected", state=FormSearch.choose_player)
        async def process_callback_button_user_selected(
            message: types.Message, state: FSMContext
        ) -> None:
            async with state.proxy() as data:
                await message.answer(
                    "Отлично! Ваше приглашение было отправлено выбранному пользователю"
                )
                await bot.send_message(
                    data["choose_player"],
                    f"Пользователю @{message.from_user.username} понравилась ваша "
                    f"карточка по игре {data['choose_game']}. Напиши ему!",
                )
            await state.finish()

        @dp.callback_query_handler(text="next_user", state=FormSearch.choose_player)
        async def process_callback_button_user_selected_final(
            call: types.CallbackQuery, state: FSMContext
        ) -> None:
            async with state.proxy() as data:
                chosen_user: UserProfile = await get_random(data)
            try:
                if chosen_user.name:
                    await call.message.answer(
                        "Мы подобрали вам пользователя:\n"
                        f"Имя пользователя: @{chosen_user.name}\n"
                        f"Инфо: {chosen_user.about}\n"
                        f"Никнейм в Steam: {chosen_user.steam_nickname}\n\n"
                        "Нажми <Выбрать пользователя> если понравилась его карточка "
                        "для отправки ему сообщения или продолжите поиск"
                        "Для выхода из поиска или изменения настроек нажмите /cancel",
                        reply_markup=markup_search,
                    )
                else:
                    await call.message.answer(
                        "Нет подходящих игроков.\n\nПопробуйте выбрать другую игру"
                    )
                    await state.finish()

            except Exception as e:
                logger.debug(e)

        @database_sync_to_async
        def get_random(data) -> UserProfile | None:
            p: UserProfile | None = (
                UserProfile.objects.filter(
                    main_game=data["choose_game"], in_search=True
                )
                .filter(~Q(external_id=data["user_id"]))
                .order_by("?")
                .first()
            )
            return p

        @database_sync_to_async
        def update_visibility(message: Message, vis: bool) -> None:
            p, _ = UserProfile.objects.get_or_create(
                external_id=message.from_user.id,
                defaults={
                    "name": message.from_user.username,
                },
            )
            p.in_search = vis
            p.save()

        @database_sync_to_async
        def user_exists(message: Message) -> bool:
            if UserProfile.objects.filter(external_id=message.from_user.id).exists():
                return True

            return False

        executor.start_polling(dispatcher=dp, skip_updates=True)
