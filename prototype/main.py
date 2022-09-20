import telebot
from telebot.types import *
from datetime import datetime
import dal.dal as db
bot = telebot.TeleBot('token')

users = {}
game_choice = {}
book_choice = {}
objects = {}

class User:
    def __init__(self, chat_id):
        self.user_id = chat_id
        self.login = ""
        self.id_user = -1
        self.campus = ""
        self.position = ""
        self.rating = ""

class Game_list:
    def __init__(self, chat_id):
        self.user_id = chat_id
        self.count = 1

class Book_list:
    def __init__(self, chat_id):
        self.user_id = chat_id
        self.count = 0

class Object:
    def __init__(self, chat_id):
        self.user_id = chat_id
        self.obj_id = 0
        self.type = ""
        self.name = ""
        self.campus = ""


@bot.message_handler(commands=["start"])
def start(message):
    markup = ReplyKeyboardMarkup()
    bot.send_message(message.chat.id, 'Привет {0.first_name}, я Bookbot'.format(message.from_user))
    msg = bot.send_message(message.chat.id, 'Представьтесь', reply_markup=markup)
    bot.register_next_step_handler(msg, check_login)

def check_login(message):
    markup = ReplyKeyboardMarkup()
    r = db.get_user(message.text)
    if r != None:
        bot.send_message(message.chat.id, 'Вход успешен', reply_markup=markup)
        position_callback(message)
    else:
        bot.send_message(message.chat.id, 'Пользователь не найден', reply_markup=markup)
        msg = bot.send_message(message.chat.id, 'Попробуйте еще раз, нужен ник слака строчными буквами', reply_markup=markup)
        bot.register_next_step_handler(msg, check_login)



def position_callback(message):
    global users
    user = User(message.chat.id)
    users[message.chat.id] = user
    r = db.get_user(message.text)
    user.id_user = r[0]
    user.position = r[1]
    user.login = r[2]
    user.campus = r[3]
    user.rating = r[5]
    r = db.get_time(user.campus)
    if user.position == 'adm':
        adm_menu(message)
    else:
        student_menu(message)


#region menu

def adm_menu(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Забронировать'))
    markup.add(KeyboardButton(text='Изменить зоны'),
               KeyboardButton(text='Репорты'),
               KeyboardButton(text='Добавить инвентарь'),
               KeyboardButton(text='Посмотреть свои брони'),
               KeyboardButton(text='Отменить бронь'))
    msg = bot.send_message(message.chat.id, 'Что сделать?', reply_markup=markup)
    bot.register_next_step_handler(msg, check_choice)

def student_menu(message):
    global users
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Забронировать'))
    markup.add(KeyboardButton(text='Посмотреть зоны'),
               KeyboardButton(text='Репорты'),
               KeyboardButton(text='Посмотреть свои брони'),
               KeyboardButton(text='Отменить бронь'))
    msg = bot.send_message(message.chat.id, 'Что сделать?', reply_markup=markup)
    bot.register_next_step_handler(msg, check_choice)

def check_choice(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    global users
    user = users[message.chat.id]
    if message.text == 'Забронировать':
        book(message)
    elif message.text == 'Изменить зоны':
        zone(message)
    elif message.text == 'Репорты':
        if user.position == 'adm':
            adm_report(message)
        else:
            student_report(message)
    elif message.text == 'Добавить инвентарь':
        add_all_inventory(message)
    elif message.text == 'Посмотреть зоны':
        show_zones(message)
    elif message.text == 'Посмотреть свои брони':
        show_bookings(message)
    elif message.text == 'Отменить бронь':
        cancel_bookings(message)
    else:
        bot.send_message(message.chat.id, 'Мы вас не поняли. Попробуйте написать еще раз.', reply_markup=markup)
        if user.position == 'adm':
            adm_menu(message)
        else:
            student_menu(message)
#endregion

#region book
def book(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    global users
    user = users[message.chat.id]
    if user.rating < 0:
        bot.send_message(message.chat.id, 'В данный момент бронирование недоступно. '
                                          'Из-за твоих поступков рейтинг доверия стал '
                                          'слишком низким. Подойди лично к АДМ, чтобы решить '
                                          'эту проблему', reply_markup=markup)
        if user.position == 'adm':
            adm_menu(message)
        else:
            student_menu(message)
    else:
        markup.add(KeyboardButton(text='Переговорка'))
        if user.position != 'abiturient':
            markup.add(KeyboardButton(text='Настольные игры'),
            KeyboardButton(text='Книги'),
            KeyboardButton(text='Инвентарь'))
            if user.position == 'adm':
                markup.add(KeyboardButton(text='Кухня'))
        markup.add( KeyboardButton(text='Назад'))
        msg = bot.send_message(message.chat.id, 'Что забронировать?', reply_markup=markup)
        bot.register_next_step_handler(msg, what_to_book)

def what_to_book(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Переговорка':
       choose_meeting_room(message)
    elif message.text == 'Настольные игры':
       choose_board_game(message)
    elif message.text == 'Книги':
        choose_book(message)
    elif message.text == 'Инвентарь':
        choose_inventory(message)
    elif message.text == 'Кухня':
        choose_kitchen(message)
    elif message.text == 'Назад':
        global users
        user = users[message.chat.id]
        if user.position == 'adm':
            adm_menu(message)
        else:
            student_menu(message)
    else:
        bot.send_message(message.chat.id, 'Мы вас не поняли. Попробуйте написать еще раз.', reply_markup=markup)
        book(message)


#region book meeting room
def choose_meeting_room(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    global users
    user = users[message.chat.id]
    if user.campus == 'kzn':
        markup.add(KeyboardButton(text='Orion'),
                   KeyboardButton(text='Liberty'),
                   KeyboardButton(text='Erehwon'),
                   KeyboardButton(text='Oasis'),
                   KeyboardButton(text='Cassiopeia'),
                   KeyboardButton(text='Летняя веранда'),
                   KeyboardButton(text='Pulsar'),
                   KeyboardButton(text='Quazar'))
        markup.add(KeyboardButton(text='Назад'))
    elif user.campus == 'msk':
        markup.add(KeyboardButton(text='Plazma'),
                   KeyboardButton(text='Акселератор'),
                   KeyboardButton(text='Зал акселератора'))
        markup.add(KeyboardButton(text='Назад'))
    elif user.campus == 'nsk':
        markup.add(KeyboardButton(text='Meeting room B'),
                   KeyboardButton(text='Meeting room C'),
                   KeyboardButton(text='Холл на 17-ом этаже'))
        markup.add(KeyboardButton(text='Назад'))
    msg = bot.send_message(message.chat.id, 'Какую переговорку забронировать?', reply_markup=markup)
    bot.register_next_step_handler(msg, available_meeting_room)


def available_meeting_room(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Назад':
        book(message)
    else:
        r = db.get_object(message.text)
        if r != None:
            get_global_object(message, r)
            show_active_booking(message, r)
            get_booking(message)
        else:
            bot.send_message(message.chat.id, 'Нет такого варианта. Попробуйте выбрать что-то другое', reply_markup=markup)
            choose_meeting_room(message)

def get_global_object(message, r):
    global objects
    object = Object(message.chat.id)
    objects[message.chat.id] = object
    object.obj_id = r[0]
    object.type = r[1]
    object.name = r[2]
    object.campus = r[5]
    object.count = r[6]
    object.available_for_students = r[7]
    object.available_for_abiturients = r[8]
    object.book_id = r[9]

def get_booking(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    msg = bot.send_message(message.chat.id, 'На какое время ходите забронировать? Формат (ГГГГ-ММ-ДД ЧЧ:ММ>ГГГГ-ММ-ДД ЧЧ:ММ)',
                     reply_markup=markup)
    bot.register_next_step_handler(msg, check_book_date)


def check_book_date(message):
    global objects
    global users
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    object = objects[message.chat.id]
    user = users[message.chat.id]
    if '>' in message.text:
        dates = message.text.split('>')
        err_true = 0
        dsn = db.check_valid_date(dates[0])
        dfn = db.check_valid_date(dates[1])
        if dsn != None and dfn != None and dsn > db.get_time(user.campus) and dfn > dsn:
            dayz = datetime.strptime(dfn, '%Y-%m-%d %H:%M:%S') - datetime.strptime(dsn, '%Y-%m-%d %H:%M:%S')
            if dayz.days > 1 or (dayz.days == 1 and dayz.seconds > 0):
                err_true = 1
            else:
                rbook = db.getbookr(object.obj_id, user.campus)
                for i in rbook:
                    if (i[1] < dsn and i[2] > dsn):
                        err_true = 1
                        break
                if err_true != 1:
                    for j in rbook:
                        if j[1] > dsn and j[1] > dfn:
                            break
                        else:
                            err_true = 1

        else:
            err_true = 1
    else:
        err_true = 1
    if err_true:
        bot.send_message(message.chat.id, 'Данные введены неверно. Попробуйте еще раз',
                         reply_markup=markup)
        get_booking(message)
    else:
        db.add_booking(user.id_user, dsn, dfn, object.obj_id)
        end_of_booking(message, 1)


def show_bookings(message):
    global users
    user = users[message.chat.id]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    booking = db.get_book_by_userid(user.id_user)
    print(booking)
    if len(booking) > 0:
        string = 'Брони:\n'
        for i in booking:
            object = db.get_object_by_id(i[4])
            string += 'Название '
            string += str(object[2])
            string += '\nНачало брони: '
            string += str(i[2])
            string += '\nКонец брони: '
            string += str(i[3])
            string += '\n'
            string += '\n'
        bot.send_message(message.chat.id, string, reply_markup=markup)
    if user.position == 'adm':
        adm_menu(message)
    else:
        student_menu(message)

def cancel_bookings(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    global users
    user = users[message.chat.id]
    if user.position == 'adm':
        markup.add(KeyboardButton(text='Отменить бронь пира'))
    markup.add(KeyboardButton(text='Отменить свою бронь'), KeyboardButton(text='Назад'))
    msg = bot.send_message(message.chat.id, 'Что сделать?', reply_markup=markup)
    bot.register_next_step_handler(msg, choose_cancel)

def cancel_my_booking(message):
    markup = ReplyKeyboardMarkup()
    global users
    user = db.get_user((users[message.chat.id]).login)
    show_someone_active_booking(message, user)
    msg = bot.send_message(message.chat.id,
                           'Напишите id бронирования, который нужно отменить. Напишите назад, чтобы выйти в меню.',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, finally_cancel_booking)

def choose_cancel(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Отменить бронь пира':
        cancel_peer_booking(message)
    elif message.text == 'Отменить свою бронь':
        cancel_my_booking(message)
    elif message.text == 'Назад':
        global users
        user = users[message.chat.id]
        if user.position == 'adm':
            adm_menu(message)
        else:
            student_menu(message)
    else:
        bot.send_message(message.chat.id, 'Нет такого варианта. Попробуйте выбрать что-то другое', reply_markup=markup)
        cancel_bookings(message)

def cancel_peer_booking(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    msg = bot.send_message(message.chat.id, 'Напишите ник человека, брони которого вы хотите отменить', reply_markup=markup)
    bot.register_next_step_handler(msg, check_username)

def cancel_my_booking(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    global users
    user = db.get_user((users[message.chat.id]).login)
    show_someone_active_booking(message, user)
    msg = bot.send_message(message.chat.id,
                           'Напишите id бронирования, который нужно отменить. Напишите назад, чтобы выйти в меню.',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, finally_cancel_booking)

def check_username(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    user = db.get_user(message.text)
    if message.text == 'Назад':
        adm_menu(message)
    else:
        if user == None:
            bot.send_message(message.chat.id,
                             'Нет человека с таким ником. Попробуйте ввести ник еще раз. Напишите Назад, чтобы выйти в главное меню.',
                             reply_markup=markup)
            cancel_peer_booking(message)
        else:
            show_someone_active_booking(message, user)
            msg = bot.send_message(message.chat.id,
                                   'Напишите id бронирования, который нужно отменить. Напишите назад, чтобы выйти в меню.',
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, finally_cancel_booking)

def show_someone_active_booking(message, user):
    string = f'Список действующих бронирований пользователя {user[2]}:'
    markup = ReplyKeyboardMarkup()
    booking = db.get_users_bookings(user[0], user[3])
    if len(booking) > 0:
        string = 'Брони:\n'
        for i in booking:
            string += 'id Брони:'
            string += str(i[0])
            string += '\nНазвание '
            string += str(i[5])
            string += '\nНачало брони: '
            string += str(i[1])
            string += '\nКонец брони: '
            string += str(i[2])
            string += '\n'
            string += '\n'
    bot.send_message(message.chat.id, string, reply_markup=markup)


def finally_cancel_booking(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    global users
    user = users[message.chat.id]
    if message.text == 'Назад':
        if user.position == 'adm':
            adm_menu(message)
        else:
            student_menu(message)
    else:
        booking = db.get_booking_by_id(message.text)
        if booking == None:
            bot.send_message(message.chat.id,
                             'Нет брони с таким ID. Попробуйте ввести число еще раз.',
                             reply_markup=markup)
            if user.position == 'adm':
                check_username(message)
            else:
                cancel_my_booking(message)
        else:
            db.remove_booking_by_id(message.text)
            bot.send_message(message.chat.id,
                             'Бронь удалена успешно.',
                             reply_markup=markup)
            if user.position == 'adm':
                adm_menu(message)
            else:
                student_menu(message)

#endregion

#region book table game
#вместо count подставить сколько всего в таблице игр, числа в наличии и доступно сейчас брать из таблицы
def choose_board_game(message):
    global game_choice

    games = db.get_all_games()
    gamec = Game_list(message.chat.id)
    game_choice[message.chat.id] = gamec
    gamec.count = 1
    page = 1
    count = db.count_games()
    markup = InlineKeyboardMarkup()

    r = db.get_object(games[gamec.count - 1][1])


    markup.add(
               InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
               InlineKeyboardButton(text=f'Вперёд --->',
                                    callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                        page + 1) + ",\"CountPage\":" + str(count) + "}"))
    msg = bot.send_message(message.chat.id, f'<b>{r[2]}</b>\n\n'
                                           f'<b>В наличии: </b><i>{r[6]}</i>\n\n'
                                           f'<b>Забронировать? Напишите:\n</b>'
                                           f'<b>Да - Забронировать игру\n</b>'
                                           f'<b>Любое сообщение - Выйти в меню бронирования\n</b>',
                                           parse_mode="HTML", reply_markup=markup)
    show_active_booking(message, r)
    bot.register_next_step_handler(msg, available_game)



@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    global game_choice

    games = db.get_all_games()
    gamec = game_choice[call.message.chat.id]
    markup = InlineKeyboardMarkup()
    json_string = json.loads(call.data)
    gamec.count = json_string['NumberPage']
    count = json_string['CountPage']
    page = json_string['NumberPage']

    r = db.get_object(games[gamec.count - 1][1])

    if page == 1:
        markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                   InlineKeyboardButton(text=f'Вперёд --->',
                                        callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                            page + 1) + ",\"CountPage\":" + str(count) + "}"))
    elif page == count:
        markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                        callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                            page - 1) + ",\"CountPage\":" + str(count) + "}"),
                   InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
    else:
        markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                        callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                            page - 1) + ",\"CountPage\":" + str(count) + "}"),
                   InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                   InlineKeyboardButton(text=f'Вперёд --->',
                                        callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                            page + 1) + ",\"CountPage\":" + str(count) + "}"))
    bot.send_message(call.message.chat.id, f'<b>{r[2]}</b>\n\n'
                                            f'<b>В наличии: </b><i>{r[6]}</i>\n\n'
                                             f'<b>Забронировать? Напишите:\n\n</b>'
                                           f'<b>Да</b> - Забронировать игру\n'
                                           f'<b>Любое сообщение</b> - Выйти в меню бронирования\n',
                           parse_mode="HTML", reply_markup=markup)
    show_active_booking(call.message, r)



@bot.callback_query_handler(lambda query: query.data == "book_game")
def available_game(message):
    if message.text == 'Да' or message.text == 'да':
        global game_choice
        gamec = game_choice[message.chat.id]
        games = db.get_all_games()
        r = db.get_object(games[gamec.count - 1][1])
        get_global_object(message, r)
        get_booking(message)
    else:
        book(message)

#endregion

#region book books
def choose_book(message):
    markup = InlineKeyboardMarkup()
    msg = bot.send_message(message.chat.id, 'Введите номер книги', reply_markup=markup)
    bot.register_next_step_handler(msg, available_book)

def available_book(message):
    book = db.get_book_by_id(message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Назад':
        global users
        user = users[message.chat.id]
        if user.position == 'adm':
            adm_menu(message)
        else:
            student_menu(message)
    else:
        if book == None:
            bot.send_message(message.chat.id, 'Книга с таким номером не была найдена, попробуйте еще раз, либо напишите Назад, чтобы Выйти в меню', reply_markup=markup)
            choose_book(message)
        else:
            get_global_object(message, book)
            get_booking(message)

#endregion

#region book inventory
def choose_inventory(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Ракетки'),
               KeyboardButton(text='Мячик для пин-понга'),
               KeyboardButton(text='Игры для Playstation'),
               KeyboardButton(text='Мини-футбол'))
    markup.add(KeyboardButton(text='Назад'))
    msg = bot.send_message(message.chat.id, 'Что из инвентаря вы хотите забронировать?', reply_markup=markup)
    bot.register_next_step_handler(msg, available_inventory)


def available_inventory(message):
    if message.text == 'Назад':
        global users
        user = users[message.chat.id]
        if user.position == 'adm':
            adm_menu(message)
        else:
            student_menu(message)
    else:
        r = db.get_object(message.text)
        show_active_booking(message, r)
        get_global_object(message, r)
        get_booking(message)
#endregion

#region book kitchen
def choose_kitchen(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Кухня на 2-ом этаже'),
               KeyboardButton(text='Кухня на 3-ем этаже'))
    msg = bot.send_message(message.chat.id, 'Какое помещение вы хотите забронировать?', reply_markup=markup)
    bot.register_next_step_handler(msg, available_kitchen)


def available_kitchen(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    r = db.get_object(message.text)
    if r != None:
        show_active_booking(message, r)
        get_global_object(message, r)
        get_booking(message)
    else:
        bot.send_message(message.chat.id, 'Нет такого варианта. Попробуйте выбрать что-то другое', reply_markup=markup)
        choose_kitchen(message)


#endregion

def end_of_booking(message, success):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if success:
        bot.send_message(message.chat.id, 'Объект забронирован!', reply_markup=markup)
        markup.add(KeyboardButton(text='Да'),
                   KeyboardButton(text='Нет'))
        msg = bot.send_message(message.chat.id, 'Забронировать что-то еще?', reply_markup=markup)
        bot.register_next_step_handler(msg, book_again)
    else:
        bot.send_message(message.chat.id, 'Объект уже забронирован или недоступен. '
                                          'Попробуйте забронировать попозже или выбрать другой вариант.',
                         reply_markup=markup)
        markup.add(KeyboardButton(text='Да'),
                   KeyboardButton(text='Нет'))
        msg = bot.send_message(message.chat.id, 'Забронировать что-то еще?', reply_markup=markup)
        bot.register_next_step_handler(msg, book_again)

def book_again(message):
    global users
    user = users[message.chat.id]

    if message.text == 'Да':
        book(message)
    else:
        if user.position == 'adm':
           adm_menu(message)
        else:
           student_menu(message)

def show_active_booking(message, r):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    global users
    user = users[message.chat.id]
    rbook = db.getbookr(r[0], user.campus)
    tablelist = ''
    bot.send_message(message.chat.id, f'Все действующие брони {r[2]}', reply_markup=markup)
    if len(rbook) > 0:
        for i in rbook:
            if i[3] == 1:
                tablelist += i[4]
            tablelist += ' '
            tablelist += i[1]
            tablelist += ' - '
            tablelist += i[2]
            tablelist += '\n'
            bot.send_message(message.chat.id, tablelist, reply_markup=markup)

#endregion

#region zones
def zone(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Зона интенсива'),
               KeyboardButton(text='Зона основы'),
               KeyboardButton(text='Недоступная зона'),
               KeyboardButton(text='Показать все зоны'))
    markup.add(KeyboardButton(text='Назад'))
    msg = bot.send_message(message.chat.id,'Какую зону изменить?', reply_markup=markup)
    bot.register_next_step_handler(msg, change_meetingroom)

def change_meetingroom(message):
    if (message.text == 'Показать все зоны'):
        show_zones(message)
    elif (message.text == 'Назад'):
        adm_menu(message)
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(text='Orion'),
                   KeyboardButton(text='Liberty'),
                   KeyboardButton(text='Erehwon'),
                   KeyboardButton(text='Oasis'),
                   KeyboardButton(text='Cassiopeia'),
                   KeyboardButton(text='Летняя веранда'),
                   KeyboardButton(text='Pulsar'),
                   KeyboardButton(text='Quazar'),
                   KeyboardButton(text='Назад'))
        msg = bot.send_message(message.chat.id, 'Нажмите, чтобы причислить переговорку к другой зоне', reply_markup=markup)
        bot.register_next_step_handler(msg, change_zone, message.text)

def change_zone(message, value):
    global users
    user = users[message.chat.id]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if (message.text != 'Назад'):
        if value == 'Зона интенсива':
            db.make_available_for_abiturients(message.text)
            bot.send_message(message.chat.id, f'{message.text} перемещен в {value}', reply_markup=markup)
        elif value == 'Зона основы' and message.text != 'Назад':
            db.make_available_for_students(message.text)
            bot.send_message(message.chat.id, f'{message.text} перемещен в {value}', reply_markup=markup)
        elif value == 'Недоступная зона':
            db.make_unvailable(message.text)
            bot.send_message(message.chat.id, f'{message.text} перемещен в {value}', reply_markup=markup)
        elif value == 'Показать все зоны' and message.text != 'Назад':
            show_zones(message)

    if message.text == 'Назад':
        if user.position == 'adm':
            adm_menu(message)
        else:
            student_menu(message)
    else:
        markup.add(KeyboardButton(text='Да'),
                   KeyboardButton(text='Нет'))
        msg = bot.send_message(message.chat.id, 'Изменить еще зону?', reply_markup=markup)
        bot.register_next_step_handler(msg, zone_again)


def show_zones(message):
    global users
    user = users[message.chat.id]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    forstudents = 'Зона основы: \n'
    forabiturients = 'Зона интенсива: \n'
    zoneabitur = db.get_book_by_available_for_abiturients(1, user.campus)
    zonestudent = db.get_book_by_available_for_students(1, user.campus)
    for i in zoneabitur:
        forabiturients += i[2]
        forabiturients += '\n'
    for i in zonestudent:
        forstudents += i[2]
        forstudents += '\n'
    bot.send_message(message.chat.id, forstudents, reply_markup=markup)
    bot.send_message(message.chat.id, forabiturients, reply_markup=markup)
    markup.add(KeyboardButton(text='Да'),
               KeyboardButton(text='Нет'))
    if user.position == 'adm':
        msg = bot.send_message(message.chat.id, 'Изменить зону?', reply_markup=markup)
        bot.register_next_step_handler(msg, zone_again)
    else:
        student_menu(message)

def zone_again(message):
    global users
    user = users[message.chat.id]

    if message.text == 'Да':
        zone(message)
    else:
        if user.position == 'adm':
           adm_menu(message)
        else:
           student_menu(message)
#endregion

#region adm_report
def adm_report(query):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Все репорты'),
               KeyboardButton(text='Логи'),
               KeyboardButton(text='Рейтинг пиров'))
    markup.add(KeyboardButton(text='Назад'))
    msg = bot.send_message(query.chat.id, 'Что показать?', reply_markup=markup)
    bot.register_next_step_handler(msg, check_report)

def check_report(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Все репорты':
        allreports(message)
    elif message.text == 'Логи':
        logs(message)
    elif message.text == 'Рейтинг пиров':
        peer_raiting(message)
    elif message.text == 'Назад':
        adm_menu(message)
    else:
        bot.send_message(message.chat.id, 'Нет такого варианта, попробуйте еще раз', reply_markup=markup)
        adm_report(message)

def allreports(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    all_reps = db.get_all_active_reports()
    string = ''
    if len(all_reps) > 0:
        for i in all_reps:
            string += 'id: '
            string += str(i[0])
            string += ' Логин = '
            string += str(i[1])
            string += ' Время = '
            string += str(i[2])
            string += ' Объект = '
            string += str(i[3])
            string += ' Сообщение = '
            string += str(i[4])
            string += '\n'
            string += '\n'
        bot.send_message(message.chat.id, string, reply_markup=markup)
    msg = bot.send_message(message.chat.id,'Введите id репорта, чтобы пометить как прочитанное', reply_markup=markup)
    bot.register_next_step_handler(msg, db.change_change_inactive_report)



def logs(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Переговорка'),
               KeyboardButton(text='Настольные игры'),
               KeyboardButton(text='Книги'),
               KeyboardButton(text='Инвентарь'),
               KeyboardButton(text='Кухня'))
    msg =  bot.send_message(message.chat.id, 'Введите категорию', reply_markup=markup)
    bot.register_next_step_handler(msg, get_logs_category)

def get_logs_category(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Переговорка':
       objes = db.get_object_by_type('meeting_room')
    elif message.text == 'Настольные игры':
       objes = db.get_object_by_type('game')
    elif message.text == 'Книги':
       objes = db.get_object_by_type('book')
    elif message.text == 'Инвентарь':
       objes = db.get_object_by_type('inventory')
    elif message.text == 'Кухня':
       objes = db.get_object_by_type('kitchen')
    string = ''
    if len(objes) > 0:
        for i in objes:
            string += 'id = '
            string += str(i[0])
            string += ' Название: '
            string += str(i[2])
            string += '\n'
        bot.send_message(message.chat.id, string, reply_markup=markup)
    msg = bot.send_message(message.chat.id, 'Укажите id объекта, чтобы посмотреть последние 10 логов (прошедшие брони)', reply_markup=markup)
    bot.register_next_step_handler(msg, print_all_logs)

def print_all_logs(message):
    global users
    user = users[message.chat.id]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    object = db.getlogs(message.text, user.position)
    string = ''
    if len(object) > 0:
        for i in object:
            string += 'id = '
            string += str(i[4])
            string += ' Логин: '
            string += str(i[5])
            string += ' Время: '
            string += str(i[1])
            string += '-'
            string += str(i[2])
            string += '\n'
        bot.send_message(message.chat.id, string, reply_markup=markup)
    adm_menu(message)


def peer_raiting(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Посмотреть общий рейтинг пиров'),
               KeyboardButton(text='Изменить рейтинг пира'))
    msg = bot.send_message(message.chat.id, 'Что сделать?', reply_markup=markup)
    bot.register_next_step_handler(msg, get_peer)

def get_peer(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Посмотреть общий рейтинг пиров':
       print_peer_raiting(message)
    elif message.text == 'Изменить рейтинг пира':
       check_peer_raiting(message)
    elif message.text == 'Назад':
        peer_raiting(message)
    else:
        bot.send_message(message.chat.id, 'Нет такого варианта, попробуйте еще раз', reply_markup=markup)
        peer_raiting(message)

def check_peer_raiting(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    msg = bot.send_message(message.chat.id, 'Напишите ник человека, рейтинг которого вы хотите увидеть', reply_markup=markup)
    bot.register_next_step_handler(msg, check_name_peer_raiting)

def check_name_peer_raiting(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    user = db.get_user(message.text)
    if message.text == 'Назад':
        adm_menu(message)
    else:
        if user == None:
            bot.send_message(message.chat.id,
                             'Нет человека с таким ником. Попробуйте ввести ник еще раз. Напишите Назад, чтобы выйти в главное меню.',
                             reply_markup=markup)
            check_peer_raiting(message)
        else:
            bot.send_message(message.chat.id,
                             f'Рейтинг пользователя {user[2]} -- {user[5]}',
                             reply_markup=markup)
        msg = bot.send_message(message.chat.id, 'Напишите насколько изменить рейтинг (только число)', reply_markup=markup)
        bot.register_next_step_handler(msg, change_peer_raiting, user)

def change_peer_raiting(message, user):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text.lstrip("-").isdigit() != True:
        bot.send_message(message.chat.id, 'Неверный ввод, попробуйте еще раз', reply_markup=markup)
        check_peer_raiting(message)
    else:
        db.sql_change_raiting(int(user[5]) + int(message.text), user[2])
        user = db.get_user(user[2])
        bot.send_message(message.chat.id, f'Теперь рейтинг {user[2]} -- {user[5]}', reply_markup=markup)
        adm_menu(message)

def print_peer_raiting(message):
    global users
    user = users[message.chat.id]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    all_students = db.get_user_by_position('student', user.campus)
    all_abituerients = db.get_user_by_position('abiturient', user.campus)
    string = 'Рейтинг:'
    if len(all_students) > 0:
        for i in all_students:
            string += 'id = '
            string += str(i[0])
            string += ' Логин: '
            string += str(i[2])
            string += ' Должность: '
            string += str(i[1])
            string += ' Рейтинг: '
            string += str(i[5])
            string += '\n'
    if len(all_abituerients) > 0:
        for j in all_abituerients:
            string += 'id = '
            string += str(j[0])
            string += ' Логин: '
            string += str(j[2])
            string += ' Должность: '
            string += str(j[1])
            string += ' Рейтинг: '
            string += str(j[5])
            string += '\n'
    bot.send_message(message.chat.id, string, reply_markup=markup)
    adm_menu(message)

#endregion

#доделать когда подключим бдшку
#region add_all_inventory
def add_all_inventory(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Настольные игры'),
            KeyboardButton(text='Книги'),
            KeyboardButton(text='Инвентарь'))
    markup.add(KeyboardButton(text='Назад'))
    msg = bot.send_message(message.chat.id, 'Что добавить?', reply_markup=markup)
    bot.register_next_step_handler(msg, choice_add)

def choice_add(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Настольные игры':
       add_games(message)
    elif message.text == 'Книги':
       add_book(message)
    elif message.text == 'Инвентарь':
       add_inventory(message)
    elif message.text == 'Назад':
       adm_menu(message)
    else:
        bot.send_message(message.chat.id, 'Нет такого вариант, попробуйте еще раз', reply_markup=markup)
        add_all_inventory(message)


def add_games(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    msg = bot.send_message(message.chat.id,
                           'Чтобы добавить игру введите через запятую с пробелом: '
                           'Название игры, описание, количество', reply_markup=markup)
    bot.register_next_step_handler(msg, check_add_inventory, message.text)

def check_add_inventory(message, value):
    global users
    user = users[message.chat.id]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    err_true = 0
    if value == 'Настольные игры':
       types = 'game'
    elif value == 'Книги':
       types = 'book'
    elif value == 'Инвентарь':
       types = 'inventory'

    if value == 'Книги':
        things = message.text.split(', ')
        if len(things) != 4:
            err_true = 1
        else:
            if things[2].isnumeric() == False and int(things[2]) <= 0:
               err_true = 1
    else:
        things = message.text.split(', ')
        if len(things) != 3:
            err_true = 1
        else:
            if things[2].isnumeric() == False and int(things[2]) <= 0:
               err_true = 1
        things.append(None)

    if err_true == 0:
        print(things[0])
        if db.validate_inventory_name(things[0]):
            db.add_game(types, things[0], things[1], user.campus, things[2], things[3])
        else:
            db.upd_count_object(things[0], things[2])
        markup.add(KeyboardButton(text='Да'))
        msg = bot.send_message(message.chat.id,
                               f'Объект типа {value} успешно добавлен\n'
                               'Напишите Да, чтобы добавить что-то еще, либо напишите любое сообщение, чтобы вернуться в меню', reply_markup=markup)
        bot.register_next_step_handler(msg, add_again)
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте ввести еще раз', reply_markup=markup)
        add_all_inventory(message)

def add_again(message):
        if message.text == 'Да':
            add_all_inventory(message)
        else:
            adm_menu(message)


def add_book(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    msg = bot.send_message(message.chat.id,
                           'Чтобы добавить книгу введите через запятую c пробелом: '
                           'Название инвентарь, описание, количество, номер книги', reply_markup=markup)
    bot.register_next_step_handler(msg, check_add_inventory, message.text)

def add_inventory(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    msg = bot.send_message(message.chat.id,
                           'Чтобы добавить инвентарь введите через запятую c пробелом: '
                           'Название инвентарь, описание, количество', reply_markup=markup)
    bot.register_next_step_handler(msg, check_add_inventory, message.text)
#endregion

# доделать когда подключим бдшку
# region student_report
def student_report(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Посмотреть репорты'),
               KeyboardButton(text='Отправить репорт о нарушении'),
               KeyboardButton(text='Отправить репорт о бронировании'))
    markup.add(KeyboardButton(text='Назад'))
    bot.send_message(message.chat.id, 'Пишите репорт о нарушении, если полученный вами инвентарь оказался'
                                      'в неподобающем состоянии (сломан, испачкан, не хватает каких-то частей)',
                     reply_markup=markup)
    msg = bot.send_message(message.chat.id,
                           'По окончании брони нужно написать отчет о бронировании, чтобы АДМ его проверили',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, check_report_choice)


def check_report_choice(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Посмотреть репорты':
        show_student_reports(message)
    elif message.text == 'Репорт (нарушение)':
        send_violation_report(message)
    elif message.text == 'Репорт (бронирование)':
        send_book_report(message)
    elif message.text == 'Назад':
        student_menu(message)
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте ввести еще раз', reply_markup=markup)
        student_report(message)


def show_student_reports(message):
    global users
    user = users[message.chat.id]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    object = db.get_all_reports_by_user(user.login)
    string = 'Репорты: '
    for i in object:
        string += 'Время отправления: '
        string += str(i[2])
        string += '\nОбъект: '
        string += str(i[3])
        string += '\nСообщение: '
        string += str(i[4])
        string += '\nСтатус (1-непрочтено, 0-прочтено): '
        string += str(i[5])
        string += '\n'
        string += '\n'
    bot.send_message(message.chat.id, string, reply_markup=markup)
    student_menu(message)


def send_violation_report(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    msg = bot.send_message(message.chat.id, 'Напишите свой комментарий к замечанию (обязательно)',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, get_text_report)

def get_text_report(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    global users
    user = users[message.chat.id]
    msg = bot.send_message(message.chat.id, 'Напишите id предмета.', reply_markup=markup)
    lastreports = db.getlast(user.id_user, user.campus)
    string = 'Для удобства список последних (прошедших и действующих) 10 броней:'
    if len(lastreports) > 0:
        for i in lastreports:
            string += 'id = '
            string += str(i[4])
            string += ' Логин: '
            string += str(i[5])
            string += ' Время: '
            string += str(i[1])
            string += '-'
            string += str(i[2])
            string += '\n'
        bot.send_message(message.chat.id, string, reply_markup=markup)
    bot.register_next_step_handler(msg, send_final_report, message)


def send_final_report(message, value):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    global users
    user = users[message.chat.id]
    dt = db.get_time(user.campus)
    objname = db.get_object_by_id(message.text)
    if objname == None:
        bot.send_message(message.chat.id, 'Предмета с таким id не существует. Попробуйте еще раз.',
                         reply_markup=markup)
        get_text_report(value)
    else:
        db.add_report(user.login, dt, objname[2], value.text)
        bot.send_message(message.chat.id, 'Отчет отправлен, будет рассмотрен АДМ в ближайшее время.',
                              reply_markup=markup)

        if user.position == 'adm':
           adm_menu(message)
        else:
           student_menu(message)


def send_book_report(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    msg = bot.send_message(message.chat.id, 'Напишите свой комментарий к репорту (обязательно)',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, get_text_report)

# endregion

@bot.message_handler(commands=["edu"])
def send_text(message):
    bot.send_photo(message.chat.id, 'https://sun9-59.userapi.com/c849324/v849324360/175f23/bC9gMSqzP3Q.jpg', caption='Сайт школы: https://edu.21-school.ru/')

#если ошибка 409 раскомментить функцию ниже:
#bot.delete_webhook()

bot.polling(none_stop=True, interval=0)
