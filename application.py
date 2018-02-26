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
    "start": "Начать использовать бота",
    "help": "Предоставит информацию о возможностях и функциях бота",
    "reset": "Запевай сначала",
    "story": "Начать погружение в удивительный мир"
}

actions_text = {
    "st_start": "Вы увидили вдалеке идущий караван и решили приблизиться к нему.",
    "st_finish_delivered": "Вы успешно помогли каравану в джунглях и получи безмерную благодарность",
    "st_finish_stealed": "Вы успешно стащили пару мелких предметов и улизнули в джунгли",
    "st_steal": "выбор, сопровождаем или грабим",
    "st_wait": "Вы приблизились к каравану. Богатые убранства поразили вас, нужно решить именно сейчас, "
               "грабить их или сопроводить в опасные джунгли",
    
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
    user.reset_step()
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = userManager.get_user(chat_id=message.chat.id)
        user.name = name
        bot.send_message(chat_id, "Знакомство завершено {name}, я знаю теперь кто ты".format(name=user.name))
        command_help(message)
        user.reset_step()
    except Exception as e:
        bot.reply_to(message, 'Упс, проблемка')


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
    user.update_pointer(facts.Pointer())
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
