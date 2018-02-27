from questgen import facts
import config
import telebot
import example

from telebot import logger
from telebot import types

logger.setLevel("INFO")

bot = telebot.TeleBot(config.token)


class User:
    def __init__(self, name):
        self.name = name
        self._pointer = facts.Pointer()
        self._step = 0
    
    def update_pointer(self, new_pointer):
        self._pointer = new_pointer
    
    def get_pointer(self):
        return self._pointer
    
    def set_step(self, step):
        self._step = step
    
    def get_step(self):
        return self._step
    
    def reset_step(self):
        self._step = 0
        
    def reset(self):
        self.reset_step()
        self.update_pointer(facts.Pointer())
        

class UserManager:
    def __init__(self):
        self._users = {}
    
    def register(self, chat_id, user):
        if chat_id in self._users:
            print('already register')
            return
        self._users[chat_id] = user
    
    def get_user(self, chat_id) -> User:
        return self._users.get(chat_id, None)


userManager = UserManager()
Story = example.story

commands = {  # command description used in the "help" command
    # "start": "Начать использовать бота",
    "help": "Предоставит информацию о возможностях и функциях бота",
    "reset": "Запевай сначала",
    "story": "Начать погружение в удивительный мир"
}

actions_text = {
    "intro": "Захотел генерал запилить дачу, большую - пребольшую. "
             "Строил - построил  да выстроил наконец. Нужно теперь порядок "
             "на участке навести да все деревья вырубить.  "
             "Рубит он деревья рубит да вырубить не может.",
    "call_colonel": "Входит полковник, широко вышагивая и чуть приподнимая бровь. "
                    "Генерал недвусмысленно намекает о проблемах и смотрит на реакцию полковника",
    "colonel_choice": "Полковнику явно неохота выполнять это поручение, но кто знает чем это закончиться?"
                      "Может получит медаль, а может хлопот докинут... Ах, была не была, полковник поступает так.",
    
    "call_captain": "Взялись за дело и рубят они рубят, да всё вырубить не могут. Задумался полковник - помощь нужна. "
                    "Вызвал он капитана, пояснил что нужно делать и вопросительно смотит на него.",
    "captain_choice": "Капитан подтянутый, молодой для своего звания."
                      "Он из тех кто цитирует 'Служить бы рад, да прислуживаться тошно' "
                      "И скорее всего его выбор будет.",
    
    "call_lieutenant": "Рубит генерал, рубил полковник, рубит капитан. Рубят всё рубят и конца не видно. "
                       "Запыхался капитан и решил что негоже лейтенанту прохлаждаться. ",
    "lieutenant_choice": "Принялся лейтенант рассуждать."
                         "Так значится, тут сё, тут то, мне бы ага. В общем решено.",
    
    "call_corporal": "Недолго лейтенант рубил, устал. Сильно. "
                     "Хлопнул себя по лбу, про эфрейтора лейтенант то позабыл совсем",
    "corporal_choice": "Пришёл эфрейтер, начал рубить и сразу заохал."
                       "Ох, да тут на месяц работы, что же делать? Как же быть?",
    
    "call_newbie": "Ну конечно, какое дело может делаться без духов?!"
                   "Рядовой прискакал и взялся за топор. Рубит и думу думает.",
    "newbie_choice": "Спина у духа ломит, портки нестираны. С другой стороны может заметят старания?",
    
    "success_finish": "Рубит генерал, рубит полковник, рубит капитан, рубит лейтенант, "
                      "рубит ефрейтор, а дух в 10 раз больше рубит и не жужжит! "
                      "Рубили рубили и срубили чёртов бесконечный лес.",
    
    "knock_to_ceo": "Решился полковник на стрёмную авантюру, настучать на генерала верхновному главнокомандующему."
                    "Того с поста сняли, привелегий лишили. Свято место пусто не бывает, тут полковника то и повысили "
                    "до генерала, а дача главнокомандующему ушла. А лес то нетронут считай, вот и решил обратиться "
                    "главнокомандующий к новоиспечённому генералу",
    "call_new_general": "Чуть ссутулившись входит новый генерал и вяло смотрит себе под ноги, он знает в чём дело и"
                        " что от него потребуют",
    "general_choice": "Генерал знает что шутки плохи и нужно выбирать разумно, с другой стороны, а что может быть хуже?",
    
    "knock_to_general": "Насмотрелся капитан на всю эту кашу и сдал полковника за такие вольности. "
                        "Генерал оценил такое рвение капитана и посвятил его в полковники вместо прошлого",
    "call_new_colonel": "Теперь уже новоиспечённый полковник заходит, но взгляды его пошатнулись. "
                        "Теперь он больше думает и размышляет",
    
    "knock_to_colonel": "Лейтенант в своей манере доложил о всём, что происходило между ним и капитаном полковнику."
                        "Не того эффекта лейтенант ожидал, капитана выгнали с позором, а лейтенант занял его место."
                        "В скором времени он понадобился полковнику",
    "call_new_captain": "Ещё не сильно освоившись, бывший лейтенант неуверенно заходит к полковнику, "
                        "догадываясь что тот прикажет ему рубить деревья",
    
    "knock_to_captain": "Ефрейтор хоть был и не сильно умный, зато ленивый. Вместо выполнения "
                        "поручения он наябеднчиал капитану. И пошло-поехало. Лейтенанта изгнали, а ефрейтер с радостью "
                        "занял его место",
    "call_new_lieutenant": "Лейтенантишко быстро зашёл к капитану и широко открыв глаза ждал приказа.",
    
    
    "dismiss_and_finish": "Отказался генерал выполнять приказ, рассверепел главнокомандующий. Разжаловали генерала, "
                          "а дачу забросили, так и стоит неопрятная и невырубленная совсем",
    
    "fail_finish": "Решил дух слинять потихому, пока рубят деревья и занятые все. Да не удалось, поймали."
                   "Посадили на губу и совсем худо стало."
                   "Вывод - делай дело и не жужжи.",
}


# handle the "/start" command
@bot.message_handler(commands=['start'])
def command_start(message):
    cid = message.chat.id
    user = userManager.get_user(chat_id=cid)
    if not user:  # if user hasn't used the "/start" command yet:
        user = User(name='Unknown')  # save user id, so you could brodcast messages to all users of this bot later
        userManager.register(cid, user)
        bot.send_message(cid, "Приветствую путник, расскажи о себе...")
        msg = bot.reply_to(message, "Как тебя зовут?")
        bot.register_next_step_handler(msg, process_name_step)
    else:
        # types.ReplyKeyboardHide()
        bot.send_message(cid, "Ты мне уже известен, не нужно представляться ещё раз!")


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    msg = bot.reply_to(message, "Что ж, начнём по-новой. Как тебя зовут?")
    user = userManager.get_user(chat_id=message.chat.id)
    user.reset()
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = userManager.get_user(chat_id=message.chat.id)
        user.name = name
        bot.send_message(chat_id, "Знакомство завершено {name}, я знаю теперь кто ты".format(name=user.name))
        command_help(message)
    except Exception as e:
        bot.reply_to(message, 'Упс, проблемка')


def again(message):
    msg = "Конец \n"
    msg += "Если хотите начать сначала нажмите /story"
    bot.send_message(message.chat.id, msg)
    
    
# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "Приведённые команды доступны: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page


@bot.message_handler(commands=['story'])
def process_story(message):
    chat_id = message.chat.id
    user = userManager.get_user(chat_id=chat_id)
    user.reset()
    msg = helper(user, message)
    bot.register_next_step_handler(msg, process_story_answer)
    
    
@bot.message_handler(content_types=["text"])
def process_story_answer(message):
    chat_id = message.chat.id
    user = userManager.get_user(chat_id=chat_id)
    if not Story.is_processed(user.get_pointer()):
        answer = message.text
        jump = Story.get_next_jump(Story.current_state(user.get_pointer()))
        if Story.need_concrete_answer(user.get_pointer()):
            jump = [j for j in jump if j.label == answer]
            
        if not jump:
            # TODO setup warning message with retry
            return
        jump = jump[0]
        user.update_pointer(new_pointer=user.get_pointer().change(state=jump.state_to))
        # final point
        if Story.is_processed(user.get_pointer()):
            bot.send_message(message.chat.id, actions_text[Story.current_state(user.get_pointer()).uid])
            again(message)
            return
        helper(user, message)


def helper(user, message):
    new_pointer, current_action, possible_jumps = Story.step(user.get_pointer())
    user.update_pointer(new_pointer=new_pointer)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True)
    markup.add(*(jump.label for jump in possible_jumps))
    msg = bot.send_message(message.chat.id, actions_text[current_action.uid], reply_markup=markup)
    return msg
    
if __name__ == '__main__':
    bot.polling(none_stop=True)
