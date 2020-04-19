import telebot
import materials as m
import keyboards as k
import json
import os

token = os.environ['TELEGRAM_TOKEN']
MAIN_STATE = 'main'
QST_STATE = 'question'
LVL_STATE = 'level'
states = json.load(open('data/states.json', 'r', encoding='utf-8'))
results = json.load(open('data/results.json', 'r', encoding='utf-8'))
level = json.load(open('data/level.json', 'r', encoding='utf-8'))
bot = telebot.TeleBot(token)


@bot.message_handler(func=lambda message: True)
def dispatcher(message):
    user_id = str(message.from_user.id)
    state = states.get(user_id, MAIN_STATE)
    json.dump(states, open('data/states.json', 'w', encoding='utf-8'), indent=2)
    if state == MAIN_STATE:
        main_handler(message)
    elif state == QST_STATE:
        question_handler(message)
    elif state == LVL_STATE:
        level_handler(message)


def main_handler(message):
    user_id = str(message.from_user.id)
    if user_id not in results.keys():
        results[user_id] = {}
        for lev in range(1, 4):
            results[user_id][str(lev)] = {"v": 0, "d": 0}
        level[user_id] = 1
        json.dump(level, open('data/level.json', 'w', encoding='utf-8'), indent=2)
        json.dump(results, open('data/results.json', 'w', encoding='utf-8'), indent=2)
    if message.text == '/start':
        bot.send_message(user_id, 'Это бот-игра в "Кто хочет стать миллионером"',
                         reply_markup=k.keyboard_main)
    elif message.text == 'Покажи счёт':
        for lev in range(1, 4):
            bot.send_message(user_id,
                             'Победы на {} уровене сложности: {}'
                             .format(lev, results[user_id][str(lev)]['v'])
                             + '\n' +
                             'Поражения на {} уровене сложности: {}'
                             .format(lev, results[user_id][str(lev)]['d']), reply_markup=k.keyboard_main)
    elif message.text == 'Обнулить счёт':
        for lev in range(1, 4):
            results[user_id][str(lev)] = {'v': 0, 'd': 0}
        bot.send_message(user_id, 'Счёт обнулён', reply_markup=k.keyboard_main)
        json.dump(results, open('data/results.json', 'w', encoding='utf-8'), indent=2)
    elif message.text == 'Привет':
        bot.send_message(user_id, 'Ну привет!', reply_markup=k.keyboard_main)
    elif message.text == 'Выбрать сложность':
        bot.send_message(user_id, 'Уровень сложности', reply_markup=k.keyboard_lvl)
        states[user_id] = LVL_STATE
        json.dump(states, open('data/states.json', 'w', encoding='utf-8'), indent=2)
    elif message.text == 'Спроси меня вопрос':
        global qst
        global ans
        global keyboard_qst
        qst = m.q_and_a(level[user_id])
        for key in qst.keys():
            ans = qst[key]
            keyboard_qst = k.keyboard_qst(ans)
            bot.send_message(user_id,
                             key, reply_markup=keyboard_qst)
        states[user_id] = QST_STATE
        json.dump(states, open('data/states.json', 'w', encoding='utf-8'), indent=2)
    else:
        bot.send_message(user_id, 'Я тебя не понял', reply_markup=k.keyboard_main)


def level_handler(message):
    user_id = str(message.from_user.id)
    if message.text == '1':
        level[user_id] = 1
        bot.send_message(user_id, 'Выбрана первая сложность', reply_markup=k.keyboard_main)
        states[user_id] = MAIN_STATE
        json.dump(states, open('data/states.json', 'w', encoding='utf-8'), indent=2)
        json.dump(level, open('data/level.json', 'w', encoding='utf-8'), indent=2)
    elif message.text == '2':
        level[user_id] = 2
        bot.send_message(user_id, 'Выбрана вторая сложность', reply_markup=k.keyboard_main)
        states[user_id] = MAIN_STATE
        json.dump(states, open('data/states.json', 'w', encoding='utf-8'), indent=2)
        json.dump(level, open('data/level.json', 'w', encoding='utf-8'), indent=2)
    elif message.text == '3':
        level[user_id] = 3
        bot.send_message(user_id, 'Выбрана третья (самая высокая) сложность', reply_markup=k.keyboard_main)
        states[user_id] = MAIN_STATE
        json.dump(states, open('data/states.json', 'w', encoding='utf-8'), indent=2)
        json.dump(level, open('data/level.json', 'w', encoding='utf-8'), indent=2)
    else:
        bot.send_message(user_id, 'Я тебя не понял', reply_markup=k.keyboard_lvl)


def question_handler(message):
    user_id = str(message.from_user.id)
    if message.text in ans[True]:
        user_id = user_id
        bot.send_message(user_id, "Правильно", reply_markup=k.keyboard_main)
        results[user_id][str(level[user_id])]['v'] += 1
        states[user_id] = MAIN_STATE
        json.dump(states, open('data/states.json', 'w', encoding='utf-8'), indent=2)
        json.dump(results, open('data/results.json', 'w', encoding='utf-8'), indent=2)
    elif message.text in ans[False]:
        user_id = user_id
        bot.send_message(user_id, "Неправильно :(" + '\n' + 'Правильный ответ: ' + ans[True],
                         reply_markup=k.keyboard_main)
        results[user_id][str(level[user_id])]['d'] += 1
        states[user_id] = MAIN_STATE
        json.dump(states, open('data/states.json', 'w', encoding='utf-8'), indent=2)
        json.dump(results, open('data/results.json', 'w', encoding='utf-8'), indent=2)
    else:
        bot.send_message(user_id, "Я тебя не понял", reply_markup=keyboard_qst)


bot.polling()