import asyncio
import logging
import sys
from os import getenv
import re
import yaml
import sqlite3, traceback, random

import aiogram.methods
from aiogram import Bot, Dispatcher, Router, types
from aiogram.methods import edit_message_text
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.markdown import hbold
import logging
from aiogram import Bot, Dispatcher, types

from bd_conn import Quests
from config import TOK, Admin_ids, Channels, user_name_bot, Group_id
from config import save_secrets, check_chat_id, read_secrets

import sys
import logging
import asyncio
import time
from io import BytesIO
import qrcode

import pytonconnect.exceptions
from pytoniq_core import Address
from pytonconnect import TonConnect

import config
from messages import get_comment_message
from connector import get_connector

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder


logger = logging.getLogger(__file__)

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv(TOK)

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

create_btn = InlineKeyboardButton(text="Создать загадку", callback_data="create")
create_markup = InlineKeyboardMarkup(inline_keyboard=[[create_btn]])

is_text, is_prize, is_answer, answer_giving, is_save, is_channels, save_quest, is_description, mr = False, False, False, False, False, False, False, False, False
n_text = ""
n_answer = ""
n_prize = ""
n_id = ''
m_id = 0
true_answer = ""
true_code = ""
true_author = ""
channels = ''
offical = ''
n_description = ''
is_ref = True
ans_id = 0
bot = Bot(TOK, parse_mode=ParseMode.HTML)
true_text, true_description, true_prize = '', '', '',


def check_sub_chanel(chat_remember):
    if chat_remember.status != 'left':
        return True
    else:
        return False


close_markup = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Прекратить", callback_data="close")]])


@dp.message(Command(commands='menu'))
async def command_menu_handler(message: Message) -> None:
    ls = [[InlineKeyboardButton(text="Создать секрет🤫", callback_data="create")],
          [InlineKeyboardButton(text="Главные секреты😎", callback_data='quests_off')],
          [InlineKeyboardButton(text="Канал со всеми секретами💎", url='https://t.me/allsecretton')],
          [InlineKeyboardButton(text="История секретов⌛️", callback_data='history_quests')],
          [InlineKeyboardButton(text="Подключить кошелек", callback_data='start')]]
    if message.from_user.id in Admin_ids:
        ls.append([InlineKeyboardButton(text="сделать массовую рассылку", callback_data="mass_ras")])
    mm_markup = InlineKeyboardMarkup(inline_keyboard=ls)
    await message.answer(f"""ALL SECRET - загадки от всех проектов на TON.🤫
Разгадывая которые вы получаете приз.💎

Здесь вы можете создать, разгадать загадку.🤔
Все функции бота снизу. Для создания официальной загадки напишите @darkdeeevil""", reply_markup=mm_markup)


@dp.message(Command(commands='start'))
async def command_start_handler(message: Message) -> None:
    global answer_giving, true_answer, true_code, true_author, ans_id, is_channels, is_text, is_description, true_text, true_description, true_prize
    ans_id = message.text.replace("/start", "").strip()
    if check_chat_id(message.from_user.id):
        secret = read_secrets()
        secret['secrets']['chat_ids'].append(message.from_user.id)
        save_secrets(secret)
    if ans_id:
        is_subscribe = 0
        ref_channels = Quests().get_channels(ans_id)
        if ref_channels:
            Channels2 = list(map(lambda x: x[1], ref_channels)) + list(map(lambda x: x.split()[1], Channels))
        else:
            Channels2 = list(map(lambda x: x.split()[1], Channels))
        for i in Channels2:
            user_channel_status = await bot.get_chat_member(chat_id=i, user_id=message.chat.id)
            user_channel_status = re.findall(r"\w*", str(user_channel_status))
            print(user_channel_status[9])
            if user_channel_status[9] != 'left':
                is_subscribe = True
            # Условие для "подписанных"
            else:
                is_subscribe = False
                break
        print(is_subscribe)
        if is_subscribe:
            quest_id = ans_id
            text, answer, prize, code, author, description = Quests().give_quest(quest_id)
            await message.answer(f"{text} (Приз: {prize})\n<em>{description}</em>",
                                 parse_mode="html", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Выйти❌", callback_data="close")]]))
            answer_giving = True
            is_description = False
            is_text = False
            true_answer = answer
            true_code = code
            true_author = author
            true_text = text
            true_description = description
            true_prize = prize
        else:
            ref_channels = Quests().get_channels(ans_id)
            if ref_channels:
                Channels2 = list(map(lambda x: x[0], ref_channels)) + list(map(lambda x: x.split()[0], Channels))
            else:
                Channels2 = list(map(lambda x: x.split()[0], Channels))
            ls = []
            for i in enumerate(Channels2):
                enum, site = i
                ls.append([InlineKeyboardButton(text=f"Подписаться🚀", url=f"{site}")])
            mk = InlineKeyboardMarkup(inline_keyboard=ls)
            await bot.send_message(text=f"Для начала разгадывания секрета, подпишитесь на каналы:",
                                   chat_id=message.chat.id, reply_markup=mk)
    else:
        ls = [[InlineKeyboardButton(text="Создать секрет🤫", callback_data="create")],
              [InlineKeyboardButton(text="Главные секреты😎", callback_data='quests_off')],
              [InlineKeyboardButton(text="Канал со всеми секретами💎", url='https://t.me/allsecretton')],
              [InlineKeyboardButton(text="История секретов⌛️", callback_data='history_quests')],
              [InlineKeyboardButton(text="Подключить кошелек", callback_data='start')]]
        if message.from_user.id in Admin_ids:
            ls.append([InlineKeyboardButton(text="сделать массовую рассылку", callback_data="mass_ras")])
        mm_markup = InlineKeyboardMarkup(inline_keyboard=ls)
        await message.answer(f"""ALL SECRET - загадки от всех проектов на TON.🤫
Разгадывая которые вы получаете приз.💎

Здесь вы можете создать, разгадать загадку.🤔
Все функции бота снизу. Для создания официальной загадки напишите @darkdeeevil""", reply_markup=mm_markup)


@dp.message()
async def message_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    global is_text, n_text, is_answer, n_answer, bot, m_id, is_prize, n_prize, answer_giving, true_answer, true_code, \
        true_author, is_save, n_id, ans_id, user_name_bot, Group_id, is_channels, channels, offical, save_quest, is_ref, is_description, n_description, true_text, true_description, true_prize, mr
    if is_description:
        n_text = message.text
        await message.delete()
        await bot.edit_message_text(
            text="<strong>Введите описание своей загадки📃:\n \n \n</strong><i>Пример: Кто создал TON?</i>",
            message_id=m_id,
            chat_id=message.chat.id,
            reply_markup=close_markup, parse_mode="html")
        is_text, is_prize, is_answer, answer_giving, is_save, is_channels, save_quest, is_description, mr = False, False, False, False, False, False, False, False, False
        is_text = True
    elif is_text:
        n_description = message.text
        await message.delete()
        await bot.edit_message_text(
            text="<strong>Введите ответ на ваш секрет🤫\n \n \n</strong><i>Пример: Павел Дуров.</i>", message_id=m_id,
            chat_id=message.chat.id,
            reply_markup=close_markup, parse_mode="html")
        is_text, is_prize, is_answer, answer_giving, is_save, is_channels, save_quest, is_description, mr = False, False, False, False, False, False, False, False, False
        is_answer = True
    elif is_answer:
        n_answer = message.text
        await message.delete()
        await bot.edit_message_text(
            text="<strong>Что получит разгадчик в награду?💎\n \n \n</strong><i>Пример: 5 USD.</i>", message_id=m_id,
            chat_id=message.chat.id,
            reply_markup=close_markup, parse_mode="html")
        is_text, is_prize, is_answer, answer_giving, is_save, is_channels, save_quest, is_description, mr = False, False, False, False, False, False, False, False, False
        if int(message.from_user.id) in Admin_ids:
            is_channels = True
        else:
            is_prize = True
            channels = ''
    elif is_channels:

        n_prize = message.text
        await message.delete()
        zxc = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="да✅", callback_data="yes")],
            [InlineKeyboardButton(text="нет❌", callback_data='no')]])
        await bot.send_message(text='Хотите ли вы добавить реферальные ссылки на каналы?', chat_id=message.chat.id,
                               reply_markup=zxc)
    elif is_prize:
        if int(message.from_user.id) in Admin_ids and is_ref:
            channels = message.text
        else:
            if not (int(message.from_user.id) in Admin_ids):
                n_prize = message.text
            channels = ''
        

        await message.delete()
        if int(message.from_user.id) in Admin_ids:
            offical = '1'
        else:
            offical = ''
        zxc = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="да✅", callback_data="save")],
            [InlineKeyboardButton(text="нет❌", callback_data='close')]])
        await bot.send_message(text='Секрет создан!\nОпубликовать?', chat_id=message.chat.id, reply_markup=zxc)
        is_text, is_prize, is_answer, answer_giving, is_save, is_channels, save_quest, is_description, mr = False, False, False, False, False, False, False, False, False

    elif answer_giving:
        leave_quest = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Выйти❌", callback_data="close")]])
        if not Quests().is_answered(ans_id):
            if message.text.lower().strip() == str(true_answer).lower().strip():
                await message.answer("Вы угадали!")
                await message.answer(f"Отправьте этот код <code>{true_code}</code> пользователю @{true_author}")

                await bot.send_message(
                    text=f'Эй, твою загадку отгадал пользователь @{message.from_user.username}.\n\n{true_text} (Приз: {true_prize})\n<em>{true_description}</em>"\n\nВот код для подтверждения <code>{true_code}</code>',
                    chat_id=Quests().get_chat_id(ans_id))
                Quests().change_is_answered(ans_id)
                answer_giving = False
            else:
                await message.answer("Ответ не верный", reply_markup=leave_quest)
        else:
            await message.answer("Эту загадку уже разгадали(", reply_markup=leave_quest)
            answer_giving = False
    elif mr:
        text_ras = message.text
        await message.delete()
        for i in read_secrets()['secrets']['chat_ids']:
            await bot.send_message(text=f'{text_ras}', chat_id=i)
        await bot.send_message(text='ваша рассылка опубликована.', chat_id=message.chat.id)
        mr = False
        is_text, is_prize, is_answer, answer_giving, is_save, is_channels, save_quest, is_description, mr = False, False, False, False, False, False, False, False, False
    else:
        await message.answer(f"Хотите создать загадку?", reply_markup=create_markup)
        is_text, is_prize, is_answer, answer_giving, is_save, is_channels, save_quest, is_description, mr = False, False, False, False, False, False, False, False, False

@dp.message(Command('connect'))
async def start_Wallet_handler(message: Message):
    chat_id = message.chat.id
    connector = get_connector(chat_id)
    connected = await connector.restore_connection()

    mk_b = InlineKeyboardBuilder()
    if connected:
        mk_b.button(text='Отправить транзакцию', callback_data='send_tr')
        mk_b.button(text='Отключить', callback_data='disconnect')
        await message.answer(text='Вы уже подключены!', reply_markup=mk_b.as_markup())

    else:
        wallets_list = TonConnect.get_wallets()
        for wallet in wallets_list:
            mk_b.button(text=wallet['name'], callback_data=f'connect:{wallet["name"]}')
        mk_b.adjust(1, )
        await message.answer(text='Выберите кошелек для подключения', reply_markup=mk_b.as_markup())

@dp.callback_query()
async def callback_handler(query: types.callback_query):
    global is_text, m_id, is_prize, is_answer, is_save, is_channels, save_quest, is_ref, answer_giving, is_description, mr, n_prize
    await query.answer()
    message = query.message
    data = query.data
    if query.data == "create":
        is_text, is_prize, is_answer, answer_giving, is_save, is_channels, save_quest, is_description, mr = False, False, False, False, False, False, False, False, False
        is_description = True
        res = await bot.send_message(
            text=f"<strong>Придумайте название вашего секрета🤔:\n \n \n</strong><i>Пример: Загадка от JET-TONS.</i>",
            chat_id=query.from_user.id, parse_mode="html", reply_markup=close_markup)
        m_id = res.message_id
    if query.data == "quests_off":
        ls = []
        if Quests().get_is_offical_quests():
            for i in Quests().get_is_offical_quests():
                id, text, prize = i
                ls.append(
                    [InlineKeyboardButton(text=f"{text} (Приз: {prize})",
                                          url=f"https://t.me/{user_name_bot}?start={id}")])
            rk = InlineKeyboardMarkup(inline_keyboard=ls)
            await bot.send_message(text=f"Официальные загадки:",
                                   chat_id=query.from_user.id, reply_markup=rk)
        else:
            await bot.send_message(text=f"Официальных загадок еще нет(:",
                                   chat_id=query.from_user.id)
    if query.data == "channels":
        await query.message.answer(text='вводите')
        msg = query.message.text
    if query.data == 'history_quests':
        spisok = []
        if Quests().get_user_quests(query.from_user.username):
            for i in Quests().get_user_quests(query.from_user.username):
                id, text, prize = i
                spisok.append(
                    [InlineKeyboardButton(text=f"{text} (Приз: {prize})",
                                          url=f"https://t.me/{user_name_bot}?start={id}")])
            rk = InlineKeyboardMarkup(inline_keyboard=spisok)
            await bot.send_message(text=f"История ваших загадок:",
                                   chat_id=query.from_user.id, reply_markup=rk)
        else:
            await bot.send_message(text=f"Вы еще не создали ни одного секрета.",
                                   chat_id=query.from_user.id, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Создать секрет🤫", callback_data="create")]]))

    if query.data == 'close':
        await query.message.delete()
        is_text, is_prize, is_answer, is_save, is_channels, answer_giving = False, False, False, False, False, False
        ls = [[InlineKeyboardButton(text="Создать секрет🤫", callback_data="create")],
              [InlineKeyboardButton(text="Главные секреты😎", callback_data='quests_off')],
              [InlineKeyboardButton(text="Канал со всеми секретами💎", url='https://t.me/allsecretton')],
              [InlineKeyboardButton(text="История секретов⌛️", callback_data='history_quests')],
              [InlineKeyboardButton(text="Подключить кошелек", callback_data='start')]]
        if query.from_user.id in Admin_ids:
            ls.append([InlineKeyboardButton(text="сделать массовую рассылку", callback_data="mass_ras")])
        mm_markup = InlineKeyboardMarkup(inline_keyboard=ls)
        await bot.send_message(text=f"""ALL SECRET - загадки от всех проектов на TON.🤫
Разгадывая которые вы получаете приз.💎

Здесь вы можете создать, разгадать загадку.🤔
Все функции бота снизу. Для создания официальной загадки напишите @darkdeeevil""",
                               chat_id=query.from_user.id, reply_markup=mm_markup)
        is_text, is_prize, is_answer, answer_giving, is_save, is_channels, save_quest, is_description, mr = False, False, False, False, False, False, False, False, False
    if query.data == 'save':
        await query.message.delete()
        q = Quests()
        q.create_quest(text=n_text, answer=n_answer, prize=n_prize, is_offical=offical,
                       author=query.from_user.username, chat_id=query.from_user.id, channels=channels,
                       description=n_description)
        n_id = q.find_quest_id()
        get_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Разгадать", url=f"https://t.me/{user_name_bot}?start={n_id[0]}")]])
        if int(query.from_user.id) in Admin_ids:
            await bot.send_message(text=f"<b>Официальная загадка!</b>"
                                        f"\n{n_text} (Приз: {n_prize})\n<em>{n_description}</em>",
                                   chat_id=Group_id[0],
                                   parse_mode="html",
                                   reply_markup=get_markup)
        else:
            await bot.send_message(
                text=f"<b>Загадка!</b>\n{n_text} (Приз: {n_prize})\n<em>{n_description}.</em>",
                chat_id=Group_id[0],
                parse_mode="html",
                reply_markup=get_markup)
        await bot.edit_message_text(text="Ваш секрет опубликован в ALL SECRET🫡", message_id=m_id,
                                    chat_id=query.from_user.id)
    if query.data == 'yes':
        await query.message.delete()
        await bot.edit_message_text(
            text="Введите ссылки на каналы таким образом:\n(ссылка id_канала)\nP.S. id_канала канала можно получить у @myidbot, переслав ему сообщение из канала. ",
            message_id=m_id, chat_id=query.from_user.id,
            reply_markup=close_markup)
        is_channels = False
        is_prize = True
    if query.data == 'no':
        channels = ''
        await query.message.delete()
        await bot.delete_message(message_id=m_id, chat_id=query.from_user.id)
        if int(query.from_user.id) in Admin_ids:
            offical = '1'
        else:
            offical = ''
        zxc = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="да✅", callback_data="save")],
            [InlineKeyboardButton(text="нет❌", callback_data='close')]])
        await bot.send_message(text='Секрет создан!\nОпубликовать?', chat_id=query.from_user.id, reply_markup=zxc)
        is_channels = False
        is_prize = True
        is_ref = False
    if query.data == 'mass_ras':
        await bot.send_message(text='Напишите сообщение которое, всем придет:', chat_id=query.from_user.id, reply_markup=close_markup)
        mr = True

async def main() -> None:
    global bot
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())