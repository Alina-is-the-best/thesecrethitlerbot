import telebot
import random
from threading import Timer

bot = telebot.TeleBot('7883139018:AAGaMHDoRfVT6K2V7FaGQwETVxrRlP2Wu2M')
user_dict = {}

# Словарь для хранения зарегистрированных пользователей и их кодов игр
registered_users = {0: {'group_title': 'haha', 'id': []},
                    1: {'group_title': 'Проверка 2', 'group_id': -1002269387767, 'id': [1195384026],
                        'names': {1195384026: 'Ponyo'}}}
# роли игроков
roles = []
# костыль всех костылей, тут типо хранится айди президента, котором отравили сообщение с выбором карты,
# а значение - это айди сообщения
user_message_ids = {}


# первое взаимодействие с ботом
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет, я бот для игры в тайного Пестеля! Используйте команду "
                          "/register, чтобы зарегистрироваться для игры.")


# промежуточный этап запроса кода игры
@bot.message_handler(commands=['register'])
def register_user(message):
    msg = bot.reply_to(message, "Пожалуйста, введите номер игры для регистрации:")
    bot.register_next_step_handler(msg, process_game_code)


def process_game_code(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    game_code = message.text

    try:
        registered_users[int(game_code)]['id'].append(user_id)
        registered_users[int(game_code)]['names'][user_id] = user_name
        # Сохраняем пользователя и код игры в словаре
        bot.reply_to(message,
                     f"{user_name}, вы успешно зарегистрированы на игру в группе {registered_users[int(game_code)]['group_title']}!")
    except Exception as e:
        bot.reply_to(message, f"{user_name}, такого номера игры не существует!")

    print(registered_users)


@bot.message_handler(func=lambda message: True)
def check_message(message):
    if 'играем' in message.text.lower():
        # блокировка добавлений новых участников, исключение из списка повторяющиеся id, 
        # проверка достаточности количества участников
        for game_code in registered_users:
            if registered_users[game_code]['group_title'] == message.chat.title:
                if len(set(registered_users[game_code]['id'])) >= 0:
                    registered_users[game_code]['id'] = set(registered_users[game_code]['id'])
                    send_private_messages(message.chat.title)
                else:
                    bot.send_message(message.chat.id,
                                     f'У вас недостаточное количество игроков, игра будет неинтересной(. '
                                     f'Минимальное количество: '
                                     f'5, текущее количество: {len(set(registered_users[game_code]["id"]))}')

    if 'начать игру' in message.text.lower():
        # Получаем имя бота
        bot_username = bot.get_me().username

        # Создаем ссылку
        bot_link = f"https://t.me/{bot_username}"

        # Создаем встроенную клавиатуру
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton("Перейти к боту", url=bot_link)
        markup.add(button)
        # добавляем в словарь с регистрацией название группы и ее номер
        group_title = message.chat.title
        registered_users[max(registered_users) + 1] = {'group_title': group_title, 'group_id': message.chat.id,
                                                       'names': {}}
        registered_users[max(registered_users)]['id'] = []

        # Отправляем сообщение с клавиатурой
        bot.send_message(message.chat.id,
                         f"Привет всем! Я - бот для игры в тайного Пестеля. \n"
                         f"Все пользователи, желающие сыграть, должны написать мне в личные сообщения команду register"
                         f"и уникальный код вашей игры - {max(registered_users)}. "
                         f"\n Когда все желающие играть, будут зарегистрированы на игру, напишите в эту группу: играть",
                         reply_markup=markup)


# отправка личных сообщений с ролью
def send_private_messages(chat_title):
    for game_code in registered_users:
        if registered_users[game_code]['group_title'] == chat_title:
            try:
                # вызов класса и присвоение ролей игрокам
                player_role = role_for_everyone(registered_users[game_code]['id'])
                registered_users[game_code]['id'] = player_role.role_for_all()

                for user_id in registered_users[game_code]['id']:
                    print(user_id, registered_users[game_code]['id'][user_id])
                    if registered_users[game_code]['id'][user_id] == 'imperial':
                        markup = telebot.types.InlineKeyboardMarkup()
                        button1 = telebot.types.InlineKeyboardButton("Выиграешь, если...",
                                                                     callback_data="имперецв")
                        button2 = telebot.types.InlineKeyboardButton("Проиграешь, если...",
                                                                     callback_data="имперецп")
                        markup.add(button1)
                        markup.add(button2)
                        # Отправляем сообщение с кнопками
                        bot.send_message(user_id, "Привет! Твоя роль: имперец", reply_markup=markup)
                    elif registered_users[game_code]['id'][user_id] == 'decembrist':
                        markup = telebot.types.InlineKeyboardMarkup()
                        button1 = telebot.types.InlineKeyboardButton("Выиграешь, если...",
                                                                     callback_data="декабриств")
                        button2 = telebot.types.InlineKeyboardButton("Проиграешь, если...",
                                                                     callback_data="декабристп")
                        markup.add(button1)
                        markup.add(button2)
                        # Отправляем сообщение с кнопками
                        bot.send_message(user_id, "Привет! Твоя роль:декабрист", reply_markup=markup)
                        # отправка ролей всех игроков
                        for i in registered_users[game_code]['id']:
                            print(i)
                            bot.send_message(user_id,
                                             f"{registered_users[game_code]['names'][i]}: {registered_users[game_code]['id'][i]}")

                    elif registered_users[game_code]['id'][user_id] == 'pestel':
                        markup = telebot.types.InlineKeyboardMarkup()
                        button1 = telebot.types.InlineKeyboardButton("Выиграешь, если",
                                                                     callback_data="Пестельв")
                        button2 = telebot.types.InlineKeyboardButton("Проиграешь, если",
                                                                     callback_data="Пестельп")
                        markup.add(button1)
                        markup.add(button2)
                        # Отправляем сообщение с кнопками
                        bot.send_message(user_id, "Привет! Твоя роль: Пестельр", reply_markup=markup)

                # выбор первых президента и канцлера
                registered_users[game_code] = first_raspred(registered_users[game_code])
                print(registered_users[game_code]['och'])
                president = registered_users[game_code]['och'][0]

                # отправка сообщения в общую группу, нде идет разглашение того, кто является президентом и канцлером
                bot.send_message(registered_users[game_code]['group_id'],
                                 f"Игра начинается, ваш первый президент: "
                                 f"{registered_users[game_code]['names'][president]}")
                # запуск основной игры
                start_game(registered_users[game_code], president)
            except Exception as e:
                print(f"Ошибка: {e}")


# нажата кнопка, я декабрист, но что это
@bot.callback_query_handler(func=lambda call: call.data == "декабриств")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Выиграешь, если: на доске будет выложено шесть Декабристских законов или после '
             'трёх принятых законов Пестель станет канцлером.', show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "декабристп")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Проиграешь, если: на доске будет выложено пять '
             'Имперских законов или Пестель будет убит.', show_alert=True)


# нажата кнопка, я имперец, но что это
@bot.callback_query_handler(func=lambda call: call.data == "имперецв")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Выиграешь, если: на доске будет выложено пять Имперских законов или '
        'Пестель будет убит.', show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "имперецп")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Проиграешь, если: на доске будет выложено шесть Декабристских законов или '
        'после трёх принятых законов Пестель станет канцлером', show_alert=True)

# нажата кнопка, я Пестель, но что это
@bot.callback_query_handler(func=lambda call: call.data == "Пестельв")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Выиграешь, если: на доске будет выложено шесть Декабристских законов или после '
             'трёх принятых декабристких законов ты станешь канцлером.', show_alert=True)
@bot.callback_query_handler(func=lambda call: call.data == "Пестельп")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Проиграешь, если: на доске будет выложено пять '
             'Имперских законов или ты будешь убит.', show_alert=True)


# нажата кнопка проверки игрока
@bot.callback_query_handler(func=lambda call: call.data[:2] == 'di')
def callback_greet(call):
    global waiting_for_answer, check_player

    user_id = call.message.chat.id
    check_player = int(call.data[2:])
    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    waiting_for_answer = 0


# нажата кнопка ликвидации игрока
@bot.callback_query_handler(func=lambda call: call.data[:2] == 'ki')
def callback_greet(call):
    global waiting_for_answer, kill_player

    user_id = call.message.chat.id
    kill_player = int(call.data[2:])
    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    waiting_for_answer = 0


# нажата кнопка выбора игрока канцлером
@bot.callback_query_handler(func=lambda call: call.data[:2] == 'id')
def callback_greet(call):
    global waiting_for_answer, chancellor

    user_id = call.message.chat.id
    chancellor = int(call.data[2:])
    print('idk')
    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    bot.send_message(call.message.chat.id, f'Вашим канцлером будет назначен: {chancellor}')
    waiting_for_answer = 0


# нажата кнопка выбора карты канцлером
@bot.callback_query_handler(func=lambda call: call.data in ['decembrist', "imperial"])
def callback_greet(call):
    global waiting_for_answer

    user_id = call.message.chat.id

    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    bot.send_message(call.message.chat.id, f'Вы выбрали: {call.data}')
    waiting_for_answer = call.data


# нажата кнопка выбора карты для исключения президентом
@bot.callback_query_handler(func=lambda call: len(call.data.split()) == 2 and call.data.split()[0] in ['decembrist', 'imperial'])
def callback_greet(call):
    global waiting_for_answer, cards_to_choose_2
    user_id = call.message.chat.id

    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    bot.send_message(call.message.chat.id, f'Я передал канцлеру данные карты: {list(call.data.split())}')
    waiting_for_answer = 0
    cards_to_choose_2 = call.data.split()


# нажата что происходит у нас есть карты а дальше
@bot.callback_query_handler(func=lambda call: call.data[2:] == 'оодекабрист')
def callback_greet(call):
    if call.data[:2] == '1 ':
        bot.answer_callback_query(
            call.id,
            text='ничего и не происходит', show_alert=True)
    elif call.data[:2] == '2 ':
        bot.answer_callback_query(
            call.id,
            text='Президент может проверить роль любого игрока', show_alert=True)
    elif call.data[:2] == '3 ':
        bot.answer_callback_query(
            call.id,
            text='Президент может назначить следующего президента по своему усмотрению', show_alert=True)
    elif call.data[:2] == '4 ':
        bot.answer_callback_query(
            call.id,
            text='Президент может убить одного игрока', show_alert=True)
    elif call.data[:2] == '5 ':
        bot.answer_callback_query(
            call.id,
            text='Президент может убить одного игрока', show_alert=True)


def first_raspred(dict_of_group):
    ochered = list(dict_of_group['id'].keys())
    random.shuffle(ochered)
    dict_of_group['och'] = ochered
    return dict_of_group


def main():
    bot.polling(none_stop=True)


def start_game(dict_of_group, president):
    global waiting_for_answer, cards_to_choose_2, chancellor, answer
    coloda = Cards()
    pole = CardsOnBoard()
    while True:
        answer = 0
        dict_of_group['rejection'] = 0
        # избрание президента и канцлера
        while answer == 0 and dict_of_group['rejection'] < 3:
            dict_of_group['rejection'] += 1
            # выбор президента
            president = dict_of_group['och'][0]
            dict_of_group['och'].append(dict_of_group['och'][0])
            dict_of_group['och'] = dict_of_group['och'][1:]

            # выбор канцлера президентом
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            kostl = []
            for i in dict_of_group['och']:
                if i != president or len(dict_of_group['och']) == 1:
                    kostl.append(telebot.types.InlineKeyboardButton(dict_of_group['names'][i],
                                                                    callback_data='id' + str(i)))

            markup.add(*kostl)

            waiting_for_answer = 1
            sent_message = bot.send_message(president,
                                            f"Президент, теперь вы можете выбрать канцлера",
                                            reply_markup=markup)

            # Сохраняем ID отправленного сообщения в памяти пользователя
            user_message_ids[president] = sent_message.message_id

            while waiting_for_answer == 1:
                pass

            waiting_for_answer = 1
            send_poll(dict_of_group['group_id'], f"Президент: {dict_of_group['names'][president]}, "
                                                 f"Канцлер: {dict_of_group['names'][chancellor]}")
            while waiting_for_answer == 1:
                pass

        # счетчик отказов на ноль
        dict_of_group['rejection'] = 0
        print('here')

        cards_to_choose = coloda.card_on_board()
        # отправляю президенту карты, которые ему выпали, добавить кнопки
        # Создаем клавиатуру
        print('here2')
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn1 = telebot.types.InlineKeyboardButton(cards_to_choose[0],
                                                  callback_data=cards_to_choose[1] + ' ' + cards_to_choose[2])
        btn2 = telebot.types.InlineKeyboardButton(cards_to_choose[1],
                                                  callback_data=cards_to_choose[0] + ' ' + cards_to_choose[2])
        btn3 = telebot.types.InlineKeyboardButton(cards_to_choose[2],
                                                  callback_data=cards_to_choose[0] + ' ' + cards_to_choose[1])
        print('here')

        # Добавляем кнопки в клавиатуру
        markup.add(btn1, btn2, btn3)

        # Отправляем сообщение с клавиатурой
        waiting_for_answer = 1
        sent_message = bot.send_message(president,
                                        f"Президент, у вас есть такие законыs: {cards_to_choose}"
                                        f", Выберите закон, от которого хотите избавиться", reply_markup=markup)

        # Сохраняем ID отправленного сообщения в памяти пользователя
        user_message_ids[president] = sent_message.message_id

        # останавливаю работу программы до его ответа
        while waiting_for_answer:
            pass
        print('мы вышли из кабалы')

        # теперь к канцлеру

        # Создаем клавиатуру
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn1 = telebot.types.InlineKeyboardButton(cards_to_choose_2[0],
                                                  callback_data=cards_to_choose_2[0])
        btn2 = telebot.types.InlineKeyboardButton(cards_to_choose_2[1],
                                                  callback_data=cards_to_choose_2[1])

        # Добавляем кнопки в клавиатуру
        markup.add(btn1, btn2)

        # Отправляем сообщение с клавиатурой
        waiting_for_answer = 1
        print('мы почти попали обратно')
        sent_message = bot.send_message(chancellor,
                                        f"Канцлер у вас на руках такие законы: {cards_to_choose_2}"
                                        f", выберите тот, который хотите выбрать", reply_markup=markup)

        # Сохраняем ID отправленного сообщения в памяти пользователя
        user_message_ids[chancellor] = sent_message.message_id

        # останавливаю работу программы до его ответа
        while waiting_for_answer == 1:
            pass
        # для единственности выполнения особенных условий
        dict_of_group['last_card'] = waiting_for_answer

        # поставить карту на поле
        pole.add(waiting_for_answer)

        onboard_imperial, onboard_decembrist = pole.check()
        print(onboard_imperial, onboard_decembrist)

        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn1 = telebot.types.InlineKeyboardButton('1 декабристская',
                                                  callback_data='1 оодекабрист')
        btn2 = telebot.types.InlineKeyboardButton('2 декабристских',
                                                  callback_data='2 оодекабрист')
        btn3 = telebot.types.InlineKeyboardButton('3 декабристских',
                                                  callback_data='3 оодекабрист')
        btn4 = telebot.types.InlineKeyboardButton('4 декабристских',
                                                  callback_data='4 оодекабрист')
        btn5 = telebot.types.InlineKeyboardButton('5 декабристских',
                                                  callback_data='5 оодекабрист')

        # Добавляем кнопки в клавиатуру
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(dict_of_group['group_id'],
                         f'Сейчас выложены {onboard_decembrist} декабристских карт и {onboard_imperial} имперских, '
                         f'чтобы узнать, что это обозначает, нажимайте на нужную кнопку.', reply_markup=markup)

        # выполнение особого протокола в зависимости от количества карт на столе
        if onboard_decembrist > 3 and dict_of_group['id'][president] == 'pestel':
            win(dict_of_group, 'decembrist')
            dict_of_group = {}

        elif onboard_decembrist == 2 and dict_of_group['last_card'] == 'decembrist':
            proverka_igroka(dict_of_group, president)

        elif onboard_decembrist == 3 and dict_of_group['last_card'] == 'decembrist':
            dict_of_group = vibor(dict_of_group, president)

        elif (onboard_decembrist == 4 or onboard_decembrist == 5) and dict_of_group['last_card'] == 'decembrist':
            died = liquidation(dict_of_group, president)
            print(died)
            if died == 'pestel':
                win(dict_of_group, 'imperial')
                dict_of_group = {}

        elif onboard_decembrist == 6:
            win(dict_of_group, 'decembrist')
            dict_of_group = {}

        elif onboard_imperial == 5:
            win(dict_of_group, 'imperial')
            dict_of_group = {}

        bot.send_message(dict_of_group['group_id'],
                         f'Теперь вы можете обсудить последствия принятых законов и ваши следующие действия. '
                         f'Следующий президент уже назначен, он может выбрать следующего канцлера, после обсуждений \n')


def win(dict_of_group, who):
    bot.send_message(dict_of_group['group_id'], f"{who} won")


def proverka_igroka(dict_of_group, president):
    global check_player, waiting_for_answer
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    kostl = []
    for i in dict_of_group['och']:
        if i != president or len(dict_of_group['och']) == 1:
            kostl.append(telebot.types.InlineKeyboardButton(dict_of_group['names'][i], callback_data='di' + str(i)))

    markup.add(*kostl)
    waiting_for_answer = 1
    sent_message = bot.send_message(president,
                                    f"Сейчас вы можете проверить сторону, которой принадлежит игрок.", reply_markup=markup)

    # Сохраняем ID отправленного сообщения в памяти пользователя
    user_message_ids[president] = sent_message.message_id

    while waiting_for_answer == 1:
        pass

    bot.send_message(president, f"Игрок {dict_of_group['names'][check_player]} - {dict_of_group['id'][check_player]}")


def vibor(dict_of_group, president):
    global check_player, waiting_for_answer
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    kostl = []
    for i in dict_of_group['och']:
        if i != president or len(dict_of_group['och']) == 1:
            kostl.append(telebot.types.InlineKeyboardButton(dict_of_group['names'][i], callback_data='di' + str(i)))

    markup.add(*kostl)
    waiting_for_answer = 1
    sent_message = bot.send_message(president,
                                    f"Теперь вы можете выбрать следующего президента", reply_markup=markup)

    # Сохраняем ID отправленного сообщения в памяти пользователя
    user_message_ids[president] = sent_message.message_id

    while waiting_for_answer == 1:
        pass

    bot.send_message(president, f"Игрок {dict_of_group['names'][check_player]} новый президент")
    ind = dict_of_group['och'].index(check_player)
    dict_of_group['och'] = dict_of_group['och'][ind:] + dict_of_group['och'][:ind]
    return dict_of_group


def liquidation(dict_of_group, president):
    global kill_player, waiting_for_answer
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    kostl = []
    for i in dict_of_group['och']:
        if i != president or len(dict_of_group['och']) == 1:
            kostl.append(telebot.types.InlineKeyboardButton(dict_of_group['names'][i], callback_data='ki' + str(i)))

    markup.add(*kostl)
    waiting_for_answer = 1
    sent_message = bot.send_message(president,
                                    f"Теперь вы можете выбрать кого убьете", reply_markup=markup)

    # Сохраняем ID отправленного сообщения в памяти пользователя
    user_message_ids[president] = sent_message.message_id

    while waiting_for_answer == 1:
        pass

    bot.send_message(president, f"Игрок {dict_of_group['names'][kill_player]} был убит")
    died = dict_of_group['id'][kill_player]

    # удаление убитого из всех списков
    del dict_of_group['names'][kill_player]
    del dict_of_group['id'][kill_player]
    dict_of_group['och'].remove(kill_player)
    print(dict_of_group)

    bot.send_message(kill_player, f"Вы были убиты")

    return died


# Функция для отправки опроса
def send_poll(GROUP_ID, stroka):
    poll_message = bot.send_poll(
        chat_id=GROUP_ID,
        question=stroka + ", Вы согласны?",
        options=["Да", "Нет"],
        is_anonymous=False
    )

    # Запускаем таймер для сбора результатов через 10 секунд
    Timer(10.0, collect_poll_results, [poll_message.chat.id, poll_message.message_id]).start()


# Функция для получения результатов опроса
def collect_poll_results(chat_id, message_id):
    global answer, waiting_for_answer
    poll_results = bot.stop_poll(chat_id, message_id)

    # Подготовка и отправка результатов
    if poll_results.options[0].voter_count > poll_results.options[1].voter_count:
        results_text = f'Президент и канцлер были выбраны'
        answer = 1
    else:
        results_text = f'('
        answer = 0

    bot.send_message(chat_id, results_text)
    waiting_for_answer = 0


class role_for_everyone:
    def __init__(self, sps: list):
        self.count_of_players = len(sps)
        self.players = list(sps)
        print(sps)
        self.players_roles = {}
        self.roles = []

    def roles_from_count(self):
        if self.count_of_players == 5:
            self.roles = ['imperial', 'imperial', 'imperial', 'decembrist', 'pestel']
        elif self.count_of_players == 6:
            self.roles = ['imperial', 'imperial', 'imperial', 'imperial', 'decembrist', 'pestel']
        elif self.count_of_players == 7:
            self.roles = ['imperial', 'imperial', 'imperial', 'imperial', 'decembrist', 'decembrist', 'pestel']
        elif self.count_of_players == 8:
            self.roles = ['imperial', 'imperial', 'imperial', 'imperial', 'imperial', 'decembrist', 'decembrist', 'pestel']
        elif self.count_of_players == 9:
            self.roles = ['imperial', 'imperial', 'imperial', 'imperial', 'imperial', 'decembrist', 'decembrist',
                          'decembrist', 'pestel']
        elif self.count_of_players == 10:
            self.roles = ['imperial', 'imperial', 'imperial', 'imperial', 'imperial', 'imperial', 'decembrist',
                          'decembrist', 'decembrist', 'pestel']
        # test
        elif self.count_of_players == 2:
            self.roles = ['decembrist', 'imperial']
        elif self.count_of_players == 1:
            self.roles = ['pestel']
        return self.roles

    def role_for_all(self):
        self.roles = self.roles_from_count()
        random.shuffle(self.roles)
        for i in range(self.count_of_players):
            self.players_roles[self.players[i]] = self.roles[i]
        print(self.players_roles)
        return self.players_roles


# Класс карточек законов
class Cards:
    def __init__(self):
        self.cards_in = ["decembrist"] * 11 + ["imperial"] * 6  # карты в колоде
        self.cards_out = []  # сюда надо складывать карты, которые откинули игроки

    # выкладка закона на стол
    def card_on_board(self):
        if len(self.cards_in) < 3:
            print(self.cards_out, self.cards_in)
            self.cards_in = self.cards_out + self.cards_in
            self.cards_out = []
            print(self.cards_out, self.cards_in)
        card = [random.choice(self.cards_in)]  # Рандомно выбираем первую карту
        self.cards_out.append(card[0])
        self.cards_in.remove(card[0])  # Удаляем 1 карту из списка карт в колоде
        card = card + [random.choice(self.cards_in)]  # Рандомно выбираем 2 карту закидываем обе карты в общий список
        self.cards_out.append(card[1])
        self.cards_in.remove(card[1])  # Удаляем 2 карту из списка
        card = card + [random.choice(self.cards_in)]  # Рандомно выбираем 3 карту закидываем три карты в общий список
        self.cards_out.append(card[2])
        self.cards_in.remove(card[2])  # Удаляем 3 карту из списка
        return card


class CardsOnBoard:
    # два списка: имперецьные карты на столе, декабристские карты на столе
    def __init__(self):

        self.onboard_imperial = 0
        self.onboard_decembrist = 0

    def add(self, card):
        if card == 'decembrist':
            self.onboard_decembrist += 1
        else:
            self.onboard_imperial += 1

    def check(self):
        return self.onboard_imperial, self.onboard_decembrist


if __name__ == "__main__":
    main()
