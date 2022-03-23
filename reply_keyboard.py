from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup


markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
buttons = ['Да', 'Нет']
markup.add(*buttons)
markup_remove = ReplyKeyboardRemove()
