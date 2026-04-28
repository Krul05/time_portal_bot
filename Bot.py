import copy
import os

import telebot
from telebot import types

from Checker import Checker
import config
from DB_manager import DB_manager
from Museum import Museum
from Quest import Quest
from Question import Question

token = os.getenv("TOKEN")

class Bot:
    bot = telebot.TeleBot(token)
    i = 1
    j = 0
    counter_of_wrong_answers = 0
    museum = Museum()
    quest_rate_id = None
    questions_arr = []
    question = Question()
    quest = Quest()
    message = None
    state = "0"
    questions_of_quest = []

    def get_bot(self):
        return self.bot

    def start_bot(self):

        def set_null():
            self.i = 1
            self.j = 0
            self.museum = Museum()
            self.quest_rate_id = None
            self.questions_arr = []
            self.question = Question()
            self.quest = Quest()
            self.message = None
            self.state = "0"
            self.questions_of_quest = []
            self.counter_of_wrong_answers = 0

        def rating(user):
            keyboard = types.InlineKeyboardMarkup()
            k1 = types.InlineKeyboardButton(text="1", callback_data="1")
            k2 = types.InlineKeyboardButton(text="2", callback_data="2")
            k3 = types.InlineKeyboardButton(text="3", callback_data="3")
            k4 = types.InlineKeyboardButton(text="4", callback_data="4")
            k5 = types.InlineKeyboardButton(text="5", callback_data="5")
            question = "Пожалуйста, оцените квест"
            keyboard.add(k1, k2, k3, k4, k5)
            self.bot.send_message(user, text=question, reply_markup=keyboard)


        def main_keyboard():
            markup = types.ReplyKeyboardMarkup(row_width=2)
            btn1 = types.KeyboardButton('/start')
            btn2 = types.KeyboardButton('/restart')
            markup.add(btn1, btn2)
            return markup

        @self.bot.message_handler(commands=['start', 'help'])
        def start(message):
            set_null()
            self.bot.send_message(message.from_user.id, "Привет!", reply_markup=main_keyboard())
            array = [['Создать квест', 'create quest'], ['Пройти квест', 'go quest']]
            question = 'Что Вы хотите сделать?'
            choose(message.from_user.id, array, question)

        @self.bot.message_handler(commands=['restart'])
        def restart(message):
            set_null()
            self.bot.send_message(message.from_user.id, "Начнём с начала!")
            array = [['Создать квест', 'create quest'], ['Пройти квест', 'go quest']]
            question1 = 'Что Вы хотите сделать?'
            choose(message.from_user.id, array, question1)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            if call.data == "create quest":
                self.bot.send_message(call.message.chat.id, 'Начнём создание')
                array = [["Наука и техника", "science"], ["Культура", "culture"], ["Другое", "other"]]
                question = "Выберите тип музея"
                choose(call.message.chat.id, array, question)
            elif call.data == "go quest":
                self.bot.send_message(call.message.chat.id, 'Введите номер квеста, который хотите пройти')
                db_manager = DB_manager()
                quests = db_manager.get_quests()
                for i in range(len(quests)):
                    self.bot.send_message(call.message.chat.id, "Номер квеста: " + str(quests[i][0]) + '\n' + "Название квеста: " + str(quests[i][1]) + "\n" + "Описание квеста: " + str(quests[i][2]) + "\n" + "Рейтинг квеста: " + str(quests[i][3]))
                self.state = config.St_id

                @self.bot.message_handler(content_types=['text'], func=lambda message: self.state == config.St_id)
                def id(message):
                    db_manager = DB_manager()
                    self.questions_of_quest = db_manager.get_questions(message.text)
                    self.quest_rate_id = message.text
                    try:
                        self.bot.send_message(message.from_user.id, self.questions_of_quest[self.j][0])
                    except:
                        self.bot.send_message(message.from_user.id, "В этом квесте нет вопросов")
                        restart(message)
                    self.state = config.St_ans_on_question

                @self.bot.message_handler(content_types=['text'],
                                          func=lambda message: self.state == config.St_ans_on_question)
                def answer_on_question(message):
                    questions = self.questions_of_quest
                    checker = Checker()
                    if checker.is_answer_correct(str(questions[self.j][0]), str(message.text), str(questions[self.j][1])):
                        self.bot.send_message(message.from_user.id, "Это правильный ответ")
                        if (len(questions) != self.j + 1):
                            self.j += 1
                            self.bot.send_message(message.from_user.id, questions[self.j][0])
                            self.state = config.St_ans_on_question
                        else:
                            self.state = config.St_wait
                            self.j = 0
                            rating(message.from_user.id)
                    elif (message.text[0] == '/'):
                        self.state = config.St_wait
                        start(message)
                    else:
                        self.counter_of_wrong_answers += 1
                        if self.counter_of_wrong_answers < 3:
                            self.bot.send_message(message.from_user.id, "Это неправильный ответ, попробуйте ещё раз")
                            self.state = config.St_ans_on_question
                        else:
                            self.counter_of_wrong_answers = 0
                            self.bot.send_message(message.from_user.id, "Это неправильный ответ. Правильный ответ: "+ str(questions[self.j][1]))
                            if (len(questions) != self.j + 1):
                                self.j += 1
                                self.bot.send_message(message.from_user.id, questions[self.j][0])
                                self.state = config.St_ans_on_question
                            else:
                                self.state = config.St_wait
                                self.j = 0
                                rating(message.from_user.id)



            elif call.data == "yes":
                save(call, self.museum, self.questions_arr, self.quest)
                set_null()
                self.bot.send_message(call.message.chat.id, 'Спасибо за создание квеста!')
                array = [['Создать квест', 'create quest'], ['Пройти квест', 'go quest']]
                question1 = 'Что Вы хотите сделать?'
                choose(call.message.chat.id, array, question1)
            elif call.data == 'no':
                set_null()
                self.bot.send_message(call.message.chat.id, 'Попробуйте ещё раз')
                array = [["Наука и техника", "science"], ["Культура", "culture"], ["Другое", "other"]]
                question = "Выберите тип музея"
                choose(call.message.chat.id, array, question)
            elif call.data == 'science' or call.data == 'culture' or call.data == 'other':
                self.museum.set_type(call.data)
                create_quest(call)
            elif call.data == '1' or call.data == '2' or call.data == '3' or call.data == '4' or call.data == '5':
                db_manager = DB_manager()
                db_manager.set_rating(call.data, self.quest_rate_id)
                self.bot.send_message(call.from_user.id, "Спасибо за прохождение теста!")
                array = [['Создать квест', 'create quest'], ['Пройти квест', 'go quest']]
                question = 'Что Вы хотите сделать?'
                choose(call.from_user.id, array, question)



        def create_quest(call):
            self.bot.send_message(call.from_user.id, "Напишите название квеста")
            self.state = config.St_name_quest

            @self.bot.message_handler(content_types=['text'], func=lambda message: self.state == config.St_name_quest)
            def name(message):
                self.quest.set_name_quest(message.text)
                self.bot.send_message(message.from_user.id, "Напишите описание для квеста")
                self.state = config.St_dis_quest

            @self.bot.message_handler(content_types=['text'], func=lambda message: self.state == config.St_dis_quest)
            def disc_quest(message):
                self.quest.set_discription(message.text)
                self.bot.send_message(message.from_user.id, "Напишите название музея")
                self.state = config.St_name_museum

            @self.bot.message_handler(content_types=['text'], func=lambda message: self.state == config.St_name_museum)
            def museum_name(message):
                self.museum.set_name_museum(message.text)
                self.bot.send_message(message.from_user.id, "Напишите ссылку на музей в картах")
                self.state = config.St_map_url

            @self.bot.message_handler(content_types=['text'], func=lambda message: self.state == config.St_map_url)
            def map_url(message):
                self.museum.set_map_url(message.text)
                if ("http://" in self.museum.map_url or "https://" in self.museum.map_url) and ("map" in self.museum.map_url or "2gis" in self.museum.map_url):
                    self.bot.send_message(message.from_user.id, "Напишите " + str(self.i) + "-й вопрос")
                    self.i += 1
                    self.state = config.St_question
                else:
                    self.bot.send_message(message.from_user.id, "Это не похоже на ссылку в картах")
                    self.bot.send_message(message.from_user.id, "Попробуйте ввести ввести ссылку из Яндекс карт, Google карт или 2gis")
                    return

            @self.bot.message_handler(content_types=['text'], func=lambda message: self.state == config.St_question)
            def questions(message):
                if message.text == "Хватит":
                    self.i = 1
                    self.state = config.St_wait
                    check(message.from_user.id, self.museum, self.questions_arr, self.quest)
                else:
                    # обработка хранения вопроса
                    self.question.set_question(message.text)
                    self.bot.send_message(message.from_user.id,
                                          "Напишите ответ на " + str(self.i - 1) + "-й вопрос")
                    self.state = config.St_answer

            @self.bot.message_handler(content_types=['text'], func=lambda message: self.state == config.St_answer)
            def answer(message):
                self.question.set_answer(message.text)
                self.questions_arr.append(copy.deepcopy(self.question))
                self.bot.send_message(message.from_user.id,
                                      "Напишите " + str(
                                          self.i) + "-й вопрос, если вопросы закончились, напишите 'Хватит'")
                self.i += 1
                self.state = config.St_question




        def check(user, museum, questions_arr, quest):
            self.bot.send_message(user, "Вот то, что ты ввёл:")
            s = "Название квеста: " + str(quest.name_quest) + "\n" + "Описание квеста: " + str(quest.discription) + "\n" + "Название музея: " + str(museum.name_museum) + "\n" + "Тип музея: " + museum.get_type() + "\n" + "Ссылка на музей: " + str(museum.map_url)
            self.bot.send_message(user, s)
            for i in range(1, len(questions_arr)+1):
                s = "Вопрос " + str(i) + ": " + str(questions_arr[i-1].question) + "\n" + "Ответ " + str(i) + ": " + str(questions_arr[i-1].answer)
                self.bot.send_message(user, s)
            array = [["Да", 'yes'], ["Нет", 'no']]
            question = "Всё правильно?"
            choose(user, array, question)


        def save(call, museum, question_arr, quest):
            db_manager = DB_manager()
            cur = db_manager.conn.cursor()
            museum_id = db_manager.addMuseum(museum, cur)
            creator_id = db_manager.addCreator(call.from_user.first_name, "@"+call.from_user.username, cur)
            quest_id = db_manager.addQuest(quest, museum_id, creator_id, cur)
            db_manager.addQuestions(question_arr, quest_id, cur)
            db_manager.conn.commit()
            cur.close()



        def choose(user, array, question):
            keyboard = types.InlineKeyboardMarkup()
            for i in range(len(array)):
                key_create = types.InlineKeyboardButton(text=array[i][0], callback_data=array[i][1])
                keyboard.add(key_create)
            self.bot.send_message(user, text=question, reply_markup=keyboard)
        self.bot.polling()



