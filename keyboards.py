from telebot import types
from random import shuffle


keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
keyboard_main.add(types.KeyboardButton('Обнулить счёт'),
                  types.KeyboardButton('Привет'),
                  types.KeyboardButton('Спроси меня вопрос'),
                  types.KeyboardButton('Покажи счёт'),
                  types.KeyboardButton('Выбрать сложность'), )


keyboard_lvl = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=3)
keyboard_lvl.add(types.KeyboardButton('1'),
                 types.KeyboardButton('2'),
                 types.KeyboardButton('3'))


def keyboard_qst(ans):
    array = []
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
    for letter in ans[False]:
        array.append(types.KeyboardButton(letter))
    array.append(types.KeyboardButton(ans[True]))
    shuffle(array)
    keyboard.add(*array)
    return keyboard
 
