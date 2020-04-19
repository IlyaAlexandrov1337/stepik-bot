import telebot
import materials as m
import keyboards as k
import json
import os
import redis

token = os.environ['TELEGRAM_TOKEN']
redis_url = os.environ.get('REDIS_URL')
MAIN_STATE = 'main'
QST_STATE = 'question'
LVL_STATE = 'level'
if redis_url is None:
    states = json.load(open('data/states.json', 'r', encoding='utf-8'))
    results = json.load(open('data/results.json', 'r', encoding='utf-8'))
    level = json.load(open('data/level.json', 'r', encoding='utf-8'))
else:
    redis_db = redis.from_url(redis_url)
    raw_states = redis_db.get('states')
    raw_results = redis_db.get('results')
    raw_level = redis_db.get('level')
    if raw_states is None:
        states = {}
    else:
        states = json.loads(raw_states)
    if raw_results is None:
        results = {}
    else:
        results = json.loads(raw_results)
    if raw_level is None:
        level = {}
    else:
        level = json.loads(raw_level)
bot = telebot.TeleBot(token)


def change_data(data, strdata):
    if redis_url is None:
        json.dump(data, open('data/{}.json'.format(strdata), 'w', encoding='utf-8'), indent=2)
    else:
        redis_data = redis.from_url(redis_url)
        redis_data.set('{}'.format(strdata), json.dumps(data))


@bot.message_handler(func=lambda message: True)
def dispatcher(message):
    user_id = str(message.from_user.id)
    state = states.get(user_id, MAIN_STATE)
    change_data(states, 'states')
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
        change_data(level, 'level')
        change_data(results, 'results')
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
        change_data(results, 'results')
    elif message.text == 'Привет':
        bot.send_message(user_id, 'Ну привет!', reply_markup=k.keyboard_main)
    elif message.text == 'Выбрать сложность':
        bot.send_message(user_id, 'Уровень сложности', reply_markup=k.keyboard_lvl)
        states[user_id] = LVL_STATE
        change_data(states, 'states')
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
        change_data(states, 'states')
    else:
        bot.send_message(user_id, 'Я тебя не понял', reply_markup=k.keyboard_main)


def level_handler(message):
    user_id = str(message.from_user.id)
    if message.text == '1':
        level[user_id] = 1
        bot.send_message(user_id, 'Выбрана первая сложность', reply_markup=k.keyboard_main)
        states[user_id] = MAIN_STATE
        change_data(states, 'states')
        change_data(level, 'level')
    elif message.text == '2':
        level[user_id] = 2
        bot.send_message(user_id, 'Выбрана вторая сложность', reply_markup=k.keyboard_main)
        states[user_id] = MAIN_STATE
        change_data(states, 'states')
        change_data(level, 'level')
    elif message.text == '3':
        level[user_id] = 3
        bot.send_message(user_id, 'Выбрана третья (самая высокая) сложность', reply_markup=k.keyboard_main)
        states[user_id] = MAIN_STATE
        change_data(states, 'states')
        change_data(level, 'level')
    else:
        bot.send_message(user_id, 'Я тебя не понял', reply_markup=k.keyboard_lvl)


def question_handler(message):
    user_id = str(message.from_user.id)
    if message.text in ans[True]:
        user_id = user_id
        bot.send_message(user_id, "Правильно", reply_markup=k.keyboard_main)
        results[user_id][str(level[user_id])]['v'] += 1
        states[user_id] = MAIN_STATE
        change_data(states, 'states')
        change_data(results, 'results')
    elif message.text in ans[False]:
        user_id = user_id
        bot.send_message(user_id, "Неправильно :(" + '\n' + 'Правильный ответ: ' + ans[True],
                         reply_markup=k.keyboard_main)
        results[user_id][str(level[user_id])]['d'] += 1
        states[user_id] = MAIN_STATE
        change_data(states, 'states')
        change_data(results, 'results')
    else:
        bot.send_message(user_id, "Я тебя не понял", reply_markup=keyboard_qst)


bot.polling()
