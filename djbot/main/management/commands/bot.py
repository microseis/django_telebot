from django.core.management.base import BaseCommand
from django.conf import settings

from aiogram import Bot, Dispatcher, executor, types
#  import asyncio
from channels.db import database_sync_to_async
from ...models import User_Profile, Game
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from ...keyboards import markup, markup_search, markup_visibility

from django.db.models import Q

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

all_games = Game.objects.all()
gameList = []

for game in all_games:
    gameList.append(game.gamename)


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

    def handle(self, *args, **options):
        bot = Bot(token=settings.TOKEN)
        dp = Dispatcher(bot, storage=storage)

        @dp.message_handler(state='*', commands=['cancel'])
        @dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
        async def cancel_handler(message: types.Message, state: FSMContext):
            """
            Allow user to cancel any action
            """
            current_state = await state.get_state()
            if current_state is None:
                return
            logging.info('Cancelling state %r', current_state)
            # Cancel state and inform user about it
            await state.finish()
            await message.answer('Ваш запрос успешно отменен.')

        @dp.callback_query_handler(text='visible')
        async def process_callback_button1(message: types.Message):
            await update_visibility(message, vis=True)
            await message.answer("Ваш профиль теперь доступен для поиска")

        @dp.callback_query_handler(text='invisible')
        async def process_callback_button2(message: types.Message):
            await update_visibility(message, vis=False)
            await message.answer("Ваш профиль больше не доступен для поиска")

        @dp.message_handler(commands=['visibility'])
        async def process_about(message: types.Message):
            await message.answer("Какую настройку видимости применить к вашему профилю?",
                                 reply_markup=markup_visibility)

        @database_sync_to_async
        def get_user_data(data, message):
            p, _ = User_Profile.objects.get_or_create(
                external_id=message.from_user.id,
                defaults={
                    'name': message.from_user.username,
                })
            p.steam_nickname = data['steam_nickname']
            p.main_game = data['main_game']
            p.about = data['about']
            p.in_search = True
            p.save()

        @database_sync_to_async
        def update_game(data, message):
            p, _ = User_Profile.objects.get_or_create(
                external_id=message.from_user.id,
                defaults={
                    'name': message.from_user.username,
                })
            p.main_game = data['choose_game']
            p.save()

        @dp.message_handler(commands=['start'])
        async def send_welcome(message: types.Message):
            if message.from_user.username:
                if await user_exists(message):
                    await message.answer(f'Рады приветствовать вас снова, {message.from_user.first_name}! \n\n'
                                         f'Для получения списка доступных команд нажмите  /help\n'
                                         f'Для выбора игры и поиска случайного соперника нажмите /play\n\n'
                                         )
                else:
                    await message.answer(
                        f'Добрый день, {message.from_user.first_name} {message.from_user.last_name}! \n\n'
                        f'Для того, чтобы начать пользоваться ботом, пожалуйста '
                        f'заполните данные о себе, нажав команду /profile')
            else:
                await message.answer("Пожалуйста установите Имя пользователя в настройках Telegram "
                                     "для начала пользования ботом. Спасибо за понимание!")

        @dp.message_handler(commands=['help'])
        async def send_welcome(message: types.Message):
            if message.from_user.username:
                await message.answer(f'Список доступных команд:\n\n'
                                     f'/start - Начало работы с ботом\n'
                                     f'/update - Редактирование данных профиля\n'
                                     f'/play - Выбор игры и соперника\n'
                                     f'/visibility - Изменение настроек видимости профиля\n'
                                     f'/cancel - Отмена выполнения запроса\n\n')
            else:
                await message.answer("Пожалуйста установите Имя пользователя в настройках Telegram "
                                     "для начала пользования ботом. Спасибо за понимание!")

        @dp.message_handler(commands=['update', 'profile'])
        async def send_update(message: types.Message):
            if message.from_user.username:
                await message.reply(f'Пожалуйста, введите данные о себе:')
                await Form.about.set()
            else:
                await message.answer("Пожалуйста установите Имя пользователя в настройках Telegram "
                                     "для начала пользования ботом. Спасибо за понимание!")

        @dp.message_handler(state=Form.about)
        async def process_about(message: types.Message, state: FSMContext):
            if len(message.text) > 2:
                async with state.proxy() as data:
                    data['about'] = message.text
                await Form.main_game.set()
                await message.answer("Отлично! В какую игру вы собираетесь поиграть?", reply_markup=markup)
            else:
                await message.answer("А вы не так многословны :). Пожалуйста напишите о себе чуть-подробнее:")

        @dp.callback_query_handler(lambda call: True, state=Form.main_game)
        async def process_game(call: types.CallbackQuery, state: FSMContext):
            async with state.proxy() as data:
                data['main_game'] = call.data
            try:
                await bot.edit_message_text(text=f"Введите ваш никнейм в Steam:",
                                            chat_id=call.message.chat.id,
                                            message_id=call.message.message_id)
                await Form.steam_nickname.set()
            except Exception as e:
                print(e)

        @dp.message_handler(state=Form.steam_nickname)
        async def process_steam(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['steam_nickname'] = message.text
            await get_user_data(data, message)
            await message.answer(f"Спасибо, вы успешно ввели следующие данные:\n\n"
                                 f"Инфо о себе: {data['about']}\n"
                                 f"Основная игра: {data['main_game']}\n"
                                 f"Никнейм в Steam: {data['steam_nickname']}\n\n"
                                 f"Для поиска игры и соперника нажмите /play")
            await state.finish()

        @dp.message_handler(commands=['play'])
        async def process_play(message: types.Message):
            if message.from_user.username:
                await FormSearch.choose_game.set()
                await message.answer("В какую игру будем играть?", reply_markup=markup)
            else:
                await message.answer("Пожалуйста установите Имя пользователя в настройках Telegram "
                                     "для начала пользования ботом. Спасибо за понимание!")

        @dp.callback_query_handler(lambda call: True, state=FormSearch.choose_game)
        async def process_choose_game(call: types.CallbackQuery, state: FSMContext):
            async with state.proxy() as data:
                data['choose_game'] = call.data
            try:
                await bot.edit_message_text(text=f"Вы выбрали игру: {call.data}\n\n"
                                                 f"Для поиска соперника нажми /search",
                                            chat_id=call.message.chat.id,
                                            message_id=call.message.message_id)
                await update_game(data, call)
                await FormSearch.choose_player.set()
            except Exception as e:
                print(e)

        @dp.message_handler(commands=['search'], state=FormSearch.choose_player)
        async def process_search(message: types.Message, state: FSMContext):
            if message.from_user.username:
                async with state.proxy() as data:
                    data['user_id'] = message.from_user.id
                #print(data['user_id'])
                chosen_user = await get_random(data)
                if chosen_user is not None:
                    async with state.proxy() as data:
                        data['choose_player'] = chosen_user.external_id
                    await message.answer(f"Мы подобрали вам пользователя:\n"
                                         f"Имя пользователя: @{chosen_user.name}\n"
                                         f"Инфо: {chosen_user.about}\n"
                                         f"Никнейм в Steam: {chosen_user.steam_nickname}\n\n"
                                         f"Нажми <Выбрать пользователя> если понравилась его карточка "
                                         f"для отправки ему сообщения или продолжите поиск\n"
                                         f"Для выхода из поиска или изменения настроек нажмите /cancel",
                                         reply_markup=markup_search)

                else:
                    await message.answer(f"Для этой игры пока что нет подходящих соперников.\n\n"
                                         f"Попробуй выбрать другую игру", reply_markup=markup)
                    await FormSearch.choose_game.set()

            else:
                await message.answer("Пожалуйста установите Имя пользователя в настройках Telegram "
                                     "для начала пользования ботом. Спасибо за понимание!")

        @dp.callback_query_handler(text='user_selected', state=FormSearch.choose_player)
        async def process_callback_button_user_selected(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                await message.answer("Отлично! Ваше приглашение было отправлено выбранному пользователю")
                await bot.send_message(data['choose_player'],
                                       f"Пользователю @{message.from_user.username} понравилась ваша "
                                       f"карточка по игре {data['choose_game']}. Напиши ему!")
            await state.finish()

        @dp.callback_query_handler(text='next_user', state=FormSearch.choose_player)
        async def process_callback_button_user_selected(call: types.CallbackQuery, state: FSMContext):
            async with state.proxy() as data:
                chosen_user = await get_random(data)
            try:
                if chosen_user.name:
                    await call.message.answer(f"Мы подобрали вам пользователя:\n"
                                              f"Имя пользователя: @{chosen_user.name}\n"
                                              f"Инфо: {chosen_user.about}\n"
                                              f"Никнейм в Steam: {chosen_user.steam_nickname}\n\n"
                                              f"Нажми <Выбрать пользователя> если понравилась его карточка "
                                              f"для отправки ему сообщения или продолжите поиск"
                                              f"Для выхода из поиска или изменения настроек нажмите /cancel",
                                              reply_markup=markup_search)
                else:
                    await call.message.answer(f"Нет подходящих игроков.\n\n"
                                              f"Попробуйте выбрать другую игру")
                    await state.finish()

            except Exception as e:
                print(e)

        @database_sync_to_async
        def get_random(data):
            p = User_Profile.objects.filter(main_game=data['choose_game'],
                                            in_search=True).filter(~Q(external_id=data['user_id'])).\
                order_by("?").first()
            return p

        @database_sync_to_async
        def update_visibility(message, vis):
            p, _ = User_Profile.objects.get_or_create(
                external_id=message.from_user.id,
                defaults={
                    'name': message.from_user.username,
                })
            p.in_search = vis
            p.save()

        @database_sync_to_async
        def user_exists(message):
            if User_Profile.objects.filter(external_id=message.from_user.id).exists():
                return True

            return False

        # loop = asyncio.get_event_loop()
        executor.start_polling(dp, skip_updates=True)
