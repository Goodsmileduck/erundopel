import os, logging
import csv
from random import shuffle, choice

from aiohttp import web
from aioalice import Dispatcher, get_new_configured_app, types
from aioalice.dispatcher import MemoryStorage, SkipHandler
from aioalice.utils.helper import Helper, HelperMode, Item
from aiohttp_healthcheck import HealthCheck
from prometheus_client import Gauge, Histogram
from prometheus_async import aio

from chatbase import track_message, track_click
from database import db
from settings import *

REQ_TIME = Histogram("response_time_seconds",
                     "time spent to response",
                     ['response'])

LOG_LEVEL_DICT = {"DEBUG": logging.DEBUG,
                  "INFO": logging.INFO,
                  "WARNING": logging.WARNING}

logging.basicConfig(
    format=u'[%(asctime)s] %(levelname)-8s  %(message)s',
    level=LOG_LEVEL_DICT[LOG_LEVEL])

# Создаем экземпляр диспетчера и подключаем хранилище в памяти
dp = Dispatcher(storage=MemoryStorage())

start_buttons = ["Давай","Не хочу"]
choose_buttons = ['один', 'два', 'три', 'повтори', 'стоп', 'помощь']

ALL_ANSWERS = [["первый", "первый вариант", "один", "1"],
               ["второй", "второй вариант", "два", "2"],
               ["третий", "третий вариант", "три", "3"]]

DIALOG_ID = '7e17c278-f191-4d77-96ec-bcd55c45a5a2'
DIALOG_URL = "https://dialogs.yandex.ru/store/skills/9d9b2484-erundopel"

REVIEW_BUTTON = {
    "title": "Поставить оценку",
    "payload": "review",
    "url": DIALOG_URL,
    "hide": False
}

greetings = ['Верно! 3 очка Гриффиндору!',
             'Правильно. 3 очка ваши!',
             'За правильный ответ - 3 очка.']

wrong_answers = ['Неверно! Попробуйте еще раз.',
                 'Неправильный ответ. Минус одно очко. Выберите другой вариант.',
                 'Неугадали. Попробуйте другой вариант.']

class States(Helper):
    mode = HelperMode.snake_case

    START = Item()

def get_words():
    logging.info('getting new words')
    words = db.words.aggregate([{'$sample': {'size': 5}}])
    return list(words)

class Message:
    def __init__(self, alice_request):
        self.user_id = alice_request.session.user_id
        self.session_id = alice_request.session.session_id
        self.command = alice_request.request.command

if LOG_LEVEL == logging.DEBUG:
    @dp.request_handler()
    async def take_all_requests(alice_request):
        # Логгируем запрос. Можно записывать в БД и тд
        logging.debug('New request! %r', alice_request)
        # Поднимаем исключение, по которому обработка перейдёт
        # к следующему хэндлеру, у которого подойдут фильтры
        raise SkipHandler

@aio.time(REQ_TIME.labels(response='ping'))
@dp.request_handler(commands='ping')
async def send_pong(alice_request):
    user_id = alice_request.session.user_id
    logging.info(f"Ping from {user_id}")
    return alice_request.response('pong')

# Новая сессия. Приветствуем пользователя
@aio.time(REQ_TIME.labels(response='start'))
@dp.request_handler(func=lambda areq: areq.session.new)
async def handle_new_session(alice_request):
    m = Message(alice_request)
    logging.info(f'Initialized new session!\nuser_id is {m.user_id!r}')
    track_message(m.user_id, m.session_id, 'start', m.command, False)
    await dp.storage.set_state(m.user_id, States.START)
    return alice_request.response(
        "Привет! Ерундопель - это игра где нужно угадать "
        "правильное определение редких слов.\n"
        "Хочешь попробовать?",
        tts="Привет! Ерундопель - это игра, где нужно угадать "
        "правильное определение редких слов. - "
        "Хочешь попробовать?",
        buttons=start_buttons)

# Не хочешь, не надо. Закрыть сессию
@dp.request_handler(commands=['нет', 'не хочу'], state=States.START)
async def handle_user_stop(alice_request):
    m = Message(alice_request)
    track_message(m.user_id, m.session_id, 'no', m.command, False)
    return alice_request.response("Жаль, возвращайтесь как решите сыграть.\n"
                                  "До встречи!",
                                  end_session=True)


#Начинаем игру
@dp.request_handler(commands=['давай', 'начать игру', 'да', 'хочу', 'начнем игру', 'еще', 'продолжить'], state=States.START)
async def handle_user_agrees(alice_request):
    m = Message(alice_request)
    await dp.storage.reset_state(m.user_id)
    track_message(m.user_id, m.session_id, 'start_game', m.command, False)
    words = get_words()
    await dp.storage.update_data(m.user_id, words_list=words)
    words_list = []
    for i in words:
        words_list.append(i["word"])
    shuffle(words_list)
    words_iter = iter(words_list)
    await dp.storage.update_data(m.user_id, words=words_iter)

    word = next(words_iter)
    exp = [element for element in words if element['word'] == word][0]
    e1 = exp["e1"]
    e2 = exp["e2"]
    e3 = exp["e3"]
    await dp.storage.update_data(m.user_id, answer=exp['a'], word=word, questions=[e1,e2,e3])
    #await dp.storage.update_data(m.user_id, answer=exp['a'])
    await dp.storage.update_data(m.user_id, points=0)
    
    return alice_request.response(
        f'Я назову слово и перечислю определения,'
        f' а вы должны выбрать один из вариантов и назвать его номер.\n'
        f'Всего будет пять слов.\n'
        f'За каждый правильный ответ, получаете 3 очка, за каждый '
        f'неправильный лишаетесь 1го очка.\n'
        f'Для завершения игры скажите "стоп".\n'
        f'Начнем!\n\n'
        f'{word} - это:\n\n'
        f'1. {e1}\n'
        f'2. {e2}\n'
        f'3. {e3}\n',
        tts='Я назову слово - и - перечислю определения'
        f' а вы должны выбрать один из вариантов и назвать его номер - .\n'
        f'Всего будет пять слов. - \n'
        f'За каждый правильный ответ, получаете 3 очка, за каждый '
        f'неправильный лишаетесь одного очка.\n'
        f'Для завершения игр+ы скажите - "стоп" -.\n'
        f'Начнем!\n\n'
        f'{word} - это:\n\n sil<[500]>'
        f'1. - {e1}\n sil<[500]> '
        f'2. - {e2}\n sil<[500]> '
        f'3. - {e3}\n sil<[500]> ',
        buttons=choose_buttons)


# Немного вариативности
@dp.request_handler(commands=['привет', 'как дела'])
async def handle_user_hi(alice_request):
    return alice_request.response(
        "Так-то мы здесь поиграть собрались, а давайте начнем игру?",
        buttons=start_buttons)

@dp.request_handler(commands=['помощь'])
async def handle_user_help(alice_request):
    m = Message(alice_request)
    track_message(m.user_id, m.session_id, 'help', m.command, False)
    return alice_request.response(
        'Cкажите номер варианта ответа, "повтори"" или "стоп".',
        buttons=choose_buttons)

@dp.request_handler(commands=['помощь', 'что ты умеешь', 'что ты умеешь?'])
async def handle_user_what(alice_request):
    m = Message(alice_request)
    track_message(m.user_id, m.session_id, 'help', m.command, False)
    return alice_request.response(
        "Я знаю много редких слов. Могу загадать тебе несколько. Хочешь попробовать?",
        buttons=start_buttons)

# Заканчиваем игру по команде
@dp.request_handler(commands=['конец игры', 'стоп', 'стой'])
async def handle_user_cancel(alice_request):
    m = Message(alice_request)
    data = await dp.storage.get_data(m.user_id)
    points = int(data.get('points'))
    return alice_request.response(
        f"Спасибо за игру!\n Вы набрали очков: {points}.\n"
        f"До встречи!",
        tts='<speaker audio="alice-sounds-game-win-1.opus">'
        f"Вы набрали очков: {points}\n - "
        f"Спасибо за игру! - "
        f"До встречи!",
        end_session=True, buttons=[REVIEW_BUTTON])


@dp.request_handler(commands=[
    "первый", "первый вариант", "один", "1",
    "второй", "второй вариант", "два", "2",
    "третий", "третий вариант", "три", "3"])
async def handle_user_answer(alice_request):
    m = Message(alice_request)
    track_message(m.user_id, m.session_id, 'choice', m.command, False)
    data = await dp.storage.get_data(m.user_id)
    words = data.get('words_list')
    words_iter = data.get('words')
    get_answer = int(data.get('answer')) - 1

    answer_list = ALL_ANSWERS[get_answer]
    if alice_request.request.command in answer_list:
        try:
            word = next(words_iter)
            exp = [element for element in words if element['word'] == word][0]
            e1 = exp["e1"]
            e2 = exp["e2"]
            e3 = exp["e3"]

            await dp.storage.update_data(m.user_id, answer=exp['a'], word=word, questions=[e1,e2,e3])
            points = int(data.get('points')) + 3
            await dp.storage.update_data(m.user_id,
                                         points=points)
            greeting = choice(greetings)
            return alice_request.response(
                f'{greeting}\n'
                f'Очки: {points}\n\n'
                f'Следующее слово.\n'
                f'{word} - это:\n\n'
                f'1. {e1}\n'
                f'2. {e2}\n'
                f'3. {e3}\n',
                tts=''
                f'{greeting}\n\n'
                f'Следующее слово.\n sil<[500]> '
                f'{word} - это:\n\n sil<[500]> '
                f'1. sil<[500]> {e1}\n sil<[500]> '
                f'2. sil<[500]> {e2}\n sil<[500]> '
                f'3. sil<[500]> {e3}\n sil<[500]> ',
                buttons=choose_buttons)
        except StopIteration:
            points = int(data.get('points')) + 3
            return alice_request.response(
                f"Вы ответили на все вопросы.\n"
                f"Спасибо за игру!\n"
                f"Вы набрали очков: {points}\n",
                tts='<speaker audio="alice-sounds-game-win-1.opus">'
                f"Вы ответили на все вопросы.\n - "
                f"Спасибо за игру!\n - "
                f"Вы набрали очков: {points}\n - ",
                end_session=True, buttons=[REVIEW_BUTTON])
    else:
        points = int(data.get('points')) -1 
        wrong_answer = choice(wrong_answers)
        await dp.storage.update_data(m.user_id,
                                     points=points)
        return alice_request.response(
            f'{wrong_answer}\n'
            f'Очки: {points}',
            tts=''
            f'{wrong_answer}',
            buttons=choose_buttons)

@dp.request_handler(commands=[
    "повтори", "повтор", "повтори пожалуйста",
    "пожалуйста повтори", "можешь повторить", "можешь повторить?"])
async def handle_user_repeat(alice_request):
    m = Message(alice_request)
    track_message(m.user_id, m.session_id, 'repeat', m.command, False)
    data = await dp.storage.get_data(m.user_id)
    questions = data.get('questions')
    word = data.get('word')
    greeting = choice(greetings)
    return alice_request.response(
        f'{word} - это:\n\n'
        f'1. {questions[0]}\n'
        f'2. {questions[1]}\n'
        f'3. {questions[2]}\n',
        tts=''
        f'{word} - это:\n\n - '
        f'1. - {questions[0]}\n - '
        f'2. - {questions[1]}\n - '
        f'3. - {questions[2]}\n - ',
        buttons=choose_buttons)

# Все остальные запросы попадают сюда
@dp.request_handler()
async def handle_all_other_requests(alice_request):
    m = Message(alice_request)
    track_message(m.user_id, m.session_id, None, m.command, True)
    return alice_request.response(
        'Cкажите номер варианта ответа, "повтори"" или "стоп".'
    )


if __name__ == '__main__':
    health = HealthCheck()
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    app.router.add_get("/healthz", health)
    app.router.add_get("/metrics", aio.web.server_stats)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)