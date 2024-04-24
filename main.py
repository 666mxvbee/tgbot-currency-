import requests
import xml.etree.ElementTree as ET
from datetime import datetime,timedelta
from aiogram import types,Bot,executor,Dispatcher
from configg import token
from aiogram.dispatcher.filters import Command, Text

current_date = datetime.today()
url = f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={current_date.strftime("%d/%m/%Y")}'
response = requests.get(url)
tree = ET.fromstring(response.content)
res = []
for currency in tree.findall('Valute'):
    name = currency.find('Name').text
    value = currency.find('Value').text
    res.append({'Name':name,'Value':value})


new_date = (datetime.today())-timedelta(days=30)
url1 = f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={new_date.strftime("%d/%m/%Y")}'
response1 = requests.get(url1)
tree1 = ET.fromstring(response1.content)
res1 = []
for currencyback in tree1.findall('Valute'):
    namelast = currencyback.find('Name').text
    valuelast = currencyback.find('Value').text
    res1.append({'Name':namelast,'Value':valuelast})

bot = Bot(token)
dp = Dispatcher(bot)
kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
b1 = types.KeyboardButton('/Currency')
kb.add(b1)


@dp.message_handler(Command('start') | Text(equals=['привет','Привет','Здравствуйте','здравствуйте','здравствуй','Здравствуй','Здарова','здарова','добрый день','Добрый день','Добрый вечер','добрый вечер']))
async def start_command(message:types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text = '<b>Приветствую! Данный бот определяет курс валют в реальном времене. Чтобы узнать курс, нажмите на появившуюся кнопку рядом с клавиатурой.\nЕсли у вас возникли вопросы по использованию бота, то можете написать /description</b>',
                           parse_mode='html',reply_markup=kb)
    await message.delete()


@dp.message_handler(commands=['description'])
async def descr_command(message:types.Message):
    await bot.send_message(chat_id=message.from_user.id,text = '<b>Нажмите на кнопку, чтобы узнать курс интересующей вам валюты. (Чтобы начать диалог с ботом заново, поздоровайтесь с ним)</b>',parse_mode='html')
    keyboard1 = types.InlineKeyboardMarkup()
    help_button = types.InlineKeyboardButton(text='Валюты',callback_data='help_button')
    keyboard1.add(help_button)
    await bot.send_message(chat_id=message.chat.id,text='<b><em>Узнать курс валют</em></b>',parse_mode='html',reply_markup=keyboard1)
    await message.delete()
    await bot.send_message(chat_id=message.chat.id,text='💰')

@dp.message_handler(commands=['currency'])
async def help_command(message:types.Message):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='Доллар США',callback_data='button1')
    button2 = types.InlineKeyboardButton(text='Евро', callback_data='button2')
    button3 = types.InlineKeyboardButton(text='Белорусский рубль', callback_data='button3')
    button4 = types.InlineKeyboardButton(text='Китайский юань', callback_data='button4')
    button5 = types.InlineKeyboardButton(text='Фунт стерлингов', callback_data='button5')
    button6 = types.InlineKeyboardButton(text='Дирхам ОАЭ', callback_data='button6')
    button7 = types.InlineKeyboardButton(text='Выйти',callback_data='button7')
    keyboard.add(button1,button2)
    keyboard.add(button3,button4)
    keyboard.add(button5,button6)
    keyboard.add(button7)
    await bot.send_message(chat_id=message.chat.id,text='<b><em>Выберите валюту</em></b>',parse_mode='html',reply_markup=keyboard)
    await message.delete()


@dp.callback_query_handler(lambda query: query.data == 'help_button')
async def button1_answer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await help_command(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button7')
async def button7_answer(callback_query:types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await start_command(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button1')
async def button1_answer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,f"<b>Курс {res[13]['Name']} - {res[13]['Value'][:5]} Руб\nАналитика рынка за прошедший месяц:\nКурс {res1[13]['Name']} - {res1[13]['Value'][:5]} Руб</b>",parse_mode='html')
    if float(res[13]['Value'][:5].replace(",","."))>float(res1[13]['Value'][:5].replace(",",".")):
        await bot.send_message(callback_query.from_user.id,f"<b>Увеличение цены на {str(float(res[13]['Value'][:5].replace(',','.'))-float(res1[13]['Value'][:5].replace(',','.')))[:4]} Руб "
                                                           f"({str((float(res[13]['Value'][:5].replace(',','.'))-float(res1[13]['Value'][:5].replace(',','.')))/float(res1[13]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>",parse_mode='html')
    else:
        await bot.send_message(callback_query.from_user.id,
                               f"<b>Уменьшение цены на {str(float(res1[13]['Value'][:5].replace(',','.'))-float(res[13]['Value'][:5].replace(',','.')))[:4]} Руб "
                               f"({str((float(res1[13]['Value'][:5].replace(',','.'))-float(res[13]['Value'][:5].replace(',','.')))/float(res[13]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над покупкой валюты</b>",
                               parse_mode='html')
    await bot.send_message(callback_query.from_user.id,text='🇺🇸')
    await help_command(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button2')
async def button2_answer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,f"<b>Курс {res[14]['Name']} - {res[14]['Value'][:5]} Руб\nАналитика рынка за прошедший месяц:\nКурс {res1[14]['Name']} - {res1[14]['Value'][:5]} Руб</b>",parse_mode='html')
    if float(res[14]['Value'][:5].replace(",","."))>float(res1[14]['Value'][:5].replace(",",".")):
        await bot.send_message(callback_query.from_user.id,f"<b>Увеличение цены на {str(float(res[14]['Value'][:5].replace(',','.'))-float(res1[14]['Value'][:5].replace(',','.')))[:4]} Руб "
                                                           f"({str((float(res[14]['Value'][:5].replace(',','.'))-float(res1[14]['Value'][:5].replace(',','.')))/float(res1[14]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>",parse_mode='html')
    else:
        await bot.send_message(callback_query.from_user.id,
                               f"<b>Уменьшение цены на {str(float(res1[14]['Value'][:5].replace(',','.'))-float(res[14]['Value'][:5].replace(',','.')))[:4]} Руб "
                               f"({str((float(res1[14]['Value'][:5].replace(',','.'))-float(res[14]['Value'][:5].replace(',','.')))/float(res[14]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над покупкой валюты</b>",
                               parse_mode='html')
    await bot.send_message(callback_query.from_user.id,text='🇪🇺')
    await help_command(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button3')
async def button3_answer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,f"<b>Курс {res[4]['Name']} - {res[4]['Value'][:5]} Руб\nАналитика рынка за прошедший месяц:\nКурс {res1[4]['Name']} - {res1[4]['Value'][:5]} Руб</b>",parse_mode='html')
    if float(res[4]['Value'][:5].replace(",","."))>float(res1[4]['Value'][:5].replace(",",".")):
        await bot.send_message(callback_query.from_user.id,f"<b>Увеличение цены на {str(float(res[4]['Value'][:5].replace(',','.'))-float(res1[4]['Value'][:5].replace(',','.')))[:4]} Руб "
                                                           f"({str((float(res[4]['Value'][:5].replace(',','.'))-float(res1[4]['Value'][:5].replace(',','.')))/float(res1[4]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>",parse_mode='html')
    else:
        await bot.send_message(callback_query.from_user.id,
                               f"<b>Уменьшение цены на {str(float(res1[4]['Value'][:5].replace(',','.'))-float(res[4]['Value'][:5].replace(',','.')))[:4]} Руб "
                               f"({str((float(res1[4]['Value'][:5].replace(',','.'))-float(res[4]['Value'][:5].replace(',','.')))/float(res[4]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над покупкой валюты</b>",
                               parse_mode='html')
    await bot.send_message(callback_query.from_user.id,text='🇧🇾')
    await help_command(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button4')
async def button4_answer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,f"<b>Курс {res[22]['Name']} - {res[22]['Value'][:5]} Руб\nАналитика рынка за прошедший месяц:\nКурс {res1[22]['Name']} - {res1[22]['Value'][:5]} Руб</b>",parse_mode='html')
    if float(res[22]['Value'][:5].replace(",","."))>float(res1[22]['Value'][:5].replace(",",".")):
        await bot.send_message(callback_query.from_user.id,f"<b>Увеличение цены на {str(float(res[22]['Value'][:5].replace(',','.'))-float(res1[22]['Value'][:5].replace(',','.')))[:4]} Руб "
                                                           f"({str((float(res[22]['Value'][:5].replace(',','.'))-float(res1[22]['Value'][:5].replace(',','.')))/float(res1[22]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>",parse_mode='html')
    else:
        await bot.send_message(callback_query.from_user.id,
                               f"<b>Уменьшение цены на {str(float(res1[22]['Value'][:5].replace(',','.'))-float(res[22]['Value'][:5].replace(',','.')))[:4]} Руб "
                               f"({str((float(res1[22]['Value'][:5].replace(',','.'))-float(res[22]['Value'][:5].replace(',','.')))/float(res[22]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над покупкой валюты</b>",
                               parse_mode='html')
    await bot.send_message(callback_query.from_user.id,text='🇨🇳')
    await help_command(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button5')
async def button5_answer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,f"<b>Курс {res[2]['Name']} - {res[2]['Value'][:5]} Руб\nАналитика рынка за прошедший месяц:\nКурс {res1[2]['Name']} - {res1[2]['Value'][:5]} Руб</b>",parse_mode='html')
    if float(res[2]['Value'][:5].replace(",","."))>float(res1[2]['Value'][:5].replace(",",".")):
        await bot.send_message(callback_query.from_user.id,f"<b>Увеличение цены на {str(float(res[2]['Value'][:5].replace(',','.'))-float(res1[2]['Value'][:5].replace(',','.')))[:4]} Руб "
                                                           f"({str((float(res[2]['Value'][:5].replace(',','.'))-float(res1[2]['Value'][:5].replace(',','.')))/float(res1[2]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>",parse_mode='html')
    else:
        await bot.send_message(callback_query.from_user.id,
                               f"<b>Уменьшение цены на {str(float(res1[2]['Value'][:5].replace(',','.'))-float(res[2]['Value'][:5].replace(',','.')))[:4]} Руб "
                               f"({str((float(res1[2]['Value'][:5].replace(',','.'))-float(res[2]['Value'][:5].replace(',','.')))/float(res[2]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над покупкой валюты</b>",
                               parse_mode='html')
    await bot.send_message(callback_query.from_user.id,text='🇬🇧')
    await help_command(callback_query.message)


@dp.callback_query_handler(lambda query: query.data == 'button6')
async def button6_answer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,f"<b>Курс {res[12]['Name']} - {res[12]['Value'][:5]} Руб\nАналитика рынка за прошедший месяц:\nКурс {res1[12]['Name']} - {res1[12]['Value'][:5]} Руб</b>",parse_mode='html')
    if float(res[12]['Value'][:5].replace(",","."))>float(res1[12]['Value'][:5].replace(",",".")):
        await bot.send_message(callback_query.from_user.id,f"<b>Увеличение цены на {str(float(res[12]['Value'][:5].replace(',','.'))-float(res1[12]['Value'][:5].replace(',','.')))[:4]} Руб "
                                                           f"({str((float(res[12]['Value'][:5].replace(',','.'))-float(res1[12]['Value'][:5].replace(',','.')))/float(res1[12]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над фиксацией прибыли</b>",parse_mode='html')
    else:
        await bot.send_message(callback_query.from_user.id,
                               f"<b>Уменьшение цены на {str(float(res1[12]['Value'][:5].replace(',','.'))-float(res[12]['Value'][:5].replace(',','.')))[:4]} Руб "
                               f"({str((float(res1[12]['Value'][:5].replace(',','.'))-float(res[12]['Value'][:5].replace(',','.')))/float(res[12]['Value'][:5].replace(',','.'))*100)[:4]}%)\nСтоит задуматься над покупкой валюты</b>",
                               parse_mode='html')
    await bot.send_message(callback_query.from_user.id,text='🇦🇪')
    await help_command(callback_query.message)


if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)
