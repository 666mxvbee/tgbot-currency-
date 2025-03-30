from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

import requests

from aiogram import types, Bot, executor, Dispatcher
from aiogram.dispatcher.filters import Command, Text
from configg import token


CURRENT_DATE = datetime.today()
URL_TODAY = (
    f"http://www.cbr.ru/scripts/XML_daily.asp?date_req="
    f"{CURRENT_DATE.strftime('%d/%m/%Y')}"
)
response = requests.get(URL_TODAY)
tree = ET.fromstring(response.content)
CURRENT_RATES = []
for currency in tree.findall('Valute'):
    name = currency.find('Name').text
    value = currency.find('Value').text
    CURRENT_RATES.append({'Name': name, 'Value': value})

PAST_DATE = datetime.today() - timedelta(days=30)
URL_30_DAYS = (
    f"http://www.cbr.ru/scripts/XML_daily.asp?date_req="
    f"{PAST_DATE.strftime('%d/%m/%Y')}"
)
response1 = requests.get(URL_30_DAYS)
tree1 = ET.fromstring(response1.content)
PAST_RATES = []
for currency in tree1.findall('Valute'):
    name = currency.find('Name').text
    value = currency.find('Value').text
    PAST_RATES.append({'Name': name, 'Value': value})

bot = Bot(token)
dp = Dispatcher(bot)

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_currency = types.KeyboardButton('/Currency')
kb.add(btn_currency)


@dp.message_handler(Command('start') | Text(
    equals=[
        'привет', 'Привет', 'Здравствуйте', 'здравствуйте',
        'здравствуй', 'Здравствуй', 'Здарова', 'здарова',
        'добрый день', 'Добрый день', 'Добрый вечер', 'добрый вечер'
    ]
))
async def start_command(message: types.Message):
    """Обработчик команды /start. Отправляет приветственное сообщение и клавиатуру."""
    welcome_text = (
        "<b>Приветствую! Данный бот определяет курс валют в реальном времени. "
        "Чтобы узнать курс, нажмите на появившуюся кнопку рядом с клавиатурой.\n"
        "Если у вас возникли вопросы по использованию бота, то можете написать /description</b>"
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=welcome_text,
        parse_mode='html',
        reply_markup=kb
    )
    await message.delete()


@dp.message_handler(commands=['description'])
async def descr_command(message: types.Message):
    """Обработчик команды /description. Выводит подробное описание функционала бота."""
    description_text = (
        "<b>Нажмите на кнопку, чтобы узнать курс интересующей вам валюты. "
        "(Чтобы начать диалог с ботом заново, поздоровайтесь с ним)</b>"
    )
    await bot.send_message(
        chat_id=message.from_user.id,
        text=description_text,
        parse_mode='html'
    )
    keyboard_inline = types.InlineKeyboardMarkup()
    help_button = types.InlineKeyboardButton(text='Валюты', callback_data='help_button')
    keyboard_inline.add(help_button)
    await bot.send_message(
        chat_id=message.chat.id,
        text='<b><em>Узнать курс валют</em></b>',
        parse_mode='html',
        reply_markup=keyboard_inline
    )
    await message.delete()
    await bot.send_message(chat_id=message.chat.id, text='💰')


@dp.message_handler(commands=['currency'])
async def currency_handler(message: types.Message):
    """Обработчик команды /currency. Показывает инлайн-клавиатуру для выбора валюты."""
    keyboard_inline = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='Доллар США', callback_data='button1')
    button2 = types.InlineKeyboardButton(text='Евро', callback_data='button2')
    button3 = types.InlineKeyboardButton(text='Белорусский рубль', callback_data='button3')
    button4 = types.InlineKeyboardButton(text='Китайский юань', callback_data='button4')
    button5 = types.InlineKeyboardButton(text='Фунт стерлингов', callback_data='button5')
    button6 = types.InlineKeyboardButton(text='Дирхам ОАЭ', callback_data='button6')
    button7 = types.InlineKeyboardButton(text='Выйти', callback_data='button7')
    keyboard_inline.add(button1, button2)
    keyboard_inline.add(button3, button4)
    keyboard_inline.add(button5, button6)
    keyboard_inline.add(button7)
    await bot.send_message(
        chat_id=message.chat.id,
        text='<b><em>Выберите валюту</em></b>',
        parse_mode='html',
        reply_markup=keyboard_inline
    )
    await message.delete()


@dp.callback_query_handler(lambda query: query.data == 'help_button')
async def help_button_handler(callback_query: types.CallbackQuery):
    """Обработчик инлайн-кнопки 'Валюты'. Переадресует на выбор валюты."""
    await bot.answer_callback_query(callback_query.id)
    await currency_handler(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button7')
async def button7_handler(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Выйти'. Возвращает к стартовому сообщению."""
    await bot.answer_callback_query(callback_query.id)
    await start_command(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button1')
async def button1_handler(callback_query: types.CallbackQuery):
    """Обработчик выбора валюты 'Доллар США'."""
    await bot.answer_callback_query(callback_query.id)
    rate_message = (
        f"<b>Курс {CURRENT_RATES[13]['Name']} - {CURRENT_RATES[13]['Value'][:5]} Руб\n"
        f"Аналитика рынка за прошедший месяц:\n"
        f"Курс {PAST_RATES[13]['Name']} - {PAST_RATES[13]['Value'][:5]} Руб</b>"
    )
    await bot.send_message(
        callback_query.from_user.id, rate_message, parse_mode='html'
    )
    current_rate = float(CURRENT_RATES[13]['Value'][:5].replace(",", "."))
    past_rate = float(PAST_RATES[13]['Value'][:5].replace(",", "."))
    if current_rate > past_rate:
        diff = current_rate - past_rate
        percent = (diff / past_rate) * 100
        advice = (
            f"<b>Увеличение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>"
        )
    else:
        diff = past_rate - current_rate
        percent = (diff / current_rate) * 100
        advice = (
            f"<b>Уменьшение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над покупкой валюты</b>"
        )
    await bot.send_message(
        callback_query.from_user.id, advice, parse_mode='html'
    )
    await bot.send_message(callback_query.from_user.id, text='🇺🇸')
    await currency_handler(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button2')
async def button2_handler(callback_query: types.CallbackQuery):
    """Обработчик выбора валюты 'Евро'."""
    await bot.answer_callback_query(callback_query.id)
    rate_message = (
        f"<b>Курс {CURRENT_RATES[14]['Name']} - {CURRENT_RATES[14]['Value'][:5]} Руб\n"
        f"Аналитика рынка за прошедший месяц:\n"
        f"Курс {PAST_RATES[14]['Name']} - {PAST_RATES[14]['Value'][:5]} Руб</b>"
    )
    await bot.send_message(
        callback_query.from_user.id, rate_message, parse_mode='html'
    )
    current_rate = float(CURRENT_RATES[14]['Value'][:5].replace(",", "."))
    past_rate = float(PAST_RATES[14]['Value'][:5].replace(",", "."))
    if current_rate > past_rate:
        diff = current_rate - past_rate
        percent = (diff / past_rate) * 100
        advice = (
            f"<b>Увеличение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>"
        )
    else:
        diff = past_rate - current_rate
        percent = (diff / current_rate) * 100
        advice = (
            f"<b>Уменьшение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над покупкой валюты</b>"
        )
    await bot.send_message(
        callback_query.from_user.id, advice, parse_mode='html'
    )
    await bot.send_message(callback_query.from_user.id, text='🇪🇺')
    await currency_handler(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button3')
async def button3_handler(callback_query: types.CallbackQuery):
    """Обработчик выбора валюты 'Белорусский рубль'."""
    await bot.answer_callback_query(callback_query.id)
    rate_message = (
        f"<b>Курс {CURRENT_RATES[4]['Name']} - {CURRENT_RATES[4]['Value'][:5]} Руб\n"
        f"Аналитика рынка за прошедший месяц:\n"
        f"Курс {PAST_RATES[4]['Name']} - {PAST_RATES[4]['Value'][:5]} Руб</b>"
    )
    await bot.send_message(
        callback_query.from_user.id, rate_message, parse_mode='html'
    )
    current_rate = float(CURRENT_RATES[4]['Value'][:5].replace(",", "."))
    past_rate = float(PAST_RATES[4]['Value'][:5].replace(",", "."))
    if current_rate > past_rate:
        diff = current_rate - past_rate
        percent = (diff / past_rate) * 100
        advice = (
            f"<b>Увеличение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>"
        )
    else:
        diff = past_rate - current_rate
        percent = (diff / current_rate) * 100
        advice = (
            f"<b>Уменьшение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над покупкой валюты</b>"
        )
    await bot.send_message(
        callback_query.from_user.id, advice, parse_mode='html'
    )
    await bot.send_message(callback_query.from_user.id, text='🇧🇾')
    await currency_handler(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button4')
async def button4_handler(callback_query: types.CallbackQuery):
    """Обработчик выбора валюты 'Китайский юань'."""
    await bot.answer_callback_query(callback_query.id)
    rate_message = (
        f"<b>Курс {CURRENT_RATES[22]['Name']} - {CURRENT_RATES[22]['Value'][:5]} Руб\n"
        f"Аналитика рынка за прошедший месяц:\n"
        f"Курс {PAST_RATES[22]['Name']} - {PAST_RATES[22]['Value'][:5]} Руб</b>"
    )
    await bot.send_message(
        callback_query.from_user.id, rate_message, parse_mode='html'
    )
    current_rate = float(CURRENT_RATES[22]['Value'][:5].replace(",", "."))
    past_rate = float(PAST_RATES[22]['Value'][:5].replace(",", "."))
    if current_rate > past_rate:
        diff = current_rate - past_rate
        percent = (diff / past_rate) * 100
        advice = (
            f"<b>Увеличение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>"
        )
    else:
        diff = past_rate - current_rate
        percent = (diff / current_rate) * 100
        advice = (
            f"<b>Уменьшение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над покупкой валюты</b>"
        )
    await bot.send_message(
        callback_query.from_user.id, advice, parse_mode='html'
    )
    await bot.send_message(callback_query.from_user.id, text='🇨🇳')
    await currency_handler(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button5')
async def button5_handler(callback_query: types.CallbackQuery):
    """Обработчик выбора валюты 'Фунт стерлингов'."""
    await bot.answer_callback_query(callback_query.id)
    rate_message = (
        f"<b>Курс {CURRENT_RATES[2]['Name']} - {CURRENT_RATES[2]['Value'][:5]} Руб\n"
        f"Аналитика рынка за прошедший месяц:\n"
        f"Курс {PAST_RATES[2]['Name']} - {PAST_RATES[2]['Value'][:5]} Руб</b>"
    )
    await bot.send_message(
        callback_query.from_user.id, rate_message, parse_mode='html'
    )
    current_rate = float(CURRENT_RATES[2]['Value'][:5].replace(",", "."))
    past_rate = float(PAST_RATES[2]['Value'][:5].replace(",", "."))
    if current_rate > past_rate:
        diff = current_rate - past_rate
        percent = (diff / past_rate) * 100
        advice = (
            f"<b>Увеличение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>"
        )
    else:
        diff = past_rate - current_rate
        percent = (diff / current_rate) * 100
        advice = (
            f"<b>Уменьшение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над покупкой валюты</b>"
        )
    await bot.send_message(
        callback_query.from_user.id, advice, parse_mode='html'
    )
    await bot.send_message(callback_query.from_user.id, text='🇬🇧')
    await currency_handler(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button6')
async def button6_handler(callback_query: types.CallbackQuery):
    """Обработчик выбора валюты 'Дирхам ОАЭ'."""
    await bot.answer_callback_query(callback_query.id)
    rate_message = (
        f"<b>Курс {CURRENT_RATES[12]['Name']} - {CURRENT_RATES[12]['Value'][:5]} Руб\n"
        f"Аналитика рынка за прошедший месяц:\n"
        f"Курс {PAST_RATES[12]['Name']} - {PAST_RATES[12]['Value'][:5]} Руб</b>"
    )
    await bot.send_message(
        callback_query.from_user.id, rate_message, parse_mode='html'
    )
    current_rate = float(CURRENT_RATES[12]['Value'][:5].replace(",", "."))
    past_rate = float(PAST_RATES[12]['Value'][:5].replace(",", "."))
    if current_rate > past_rate:
        diff = current_rate - past_rate
        percent = (diff / past_rate) * 100
        advice = (
            f"<b>Увеличение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>"
        )
    else:
        diff = past_rate - current_rate
        percent = (diff / current_rate) * 100
        advice = (
            f"<b>Уменьшение цены на {str(diff)[:4]} Руб "
            f"({str(percent)[:4]}%)\nСтоит задуматься над покупкой валюты</b>"
        )
    await bot.send_message(
        callback_query.from_user.id, advice, parse_mode='html'
    )
    await bot.send_message(callback_query.from_user.id, text='🇦🇪')
    await currency_handler(callback_query.message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
