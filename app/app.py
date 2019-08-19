import os, logging
import csv
from random import shuffle

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


LOG_LEVEL_DICT = {"DEBUG": logging.DEBUG,
                  "INFO": logging.INFO,
                  "WARNING": logging.WARNING}

logging.basicConfig(
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    level=LOG_LEVEL_DICT[LOG_LEVEL])

# Создаем экземпляр диспетчера и подключаем хранилище в памяти
dp = Dispatcher(storage=MemoryStorage())

start_buttons = ["Давай","Не хочу"]
choose_buttons = ['первый', 'второй', 'третий', 'конец игры']

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

def get_words():
    words = db.words.aggregate([{ $sample: { size: 5 } }])
    return words

class Message:
    def create(self, alice_request)
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

# Новая сессия. Приветствуем пользователя
@aio.time(REQ_TIME.labels(response='start'))
@dp.request_handler(func=lambda areq: areq.session.new)
async def handle_new_session(alice_request):
    m = Message.create(alice_request)
    logging.info(f'Initialized new session!\nuser_id is {m.user_id!r}')
    track_message(m.user_id, m.session_id, 'start', m.command, False)
    return alice_request.response(
        "Привет! Ерундопель - это игра где нужно угадать "
        "правильное определение редких слов.\n"
        "Хочешь попробовать?",
        tts="Привет! Ерундопель - это игра, где нужно угадать "
        "правильное определение редких слов. - "
        "Хочешь попробовать?",
        buttons=start_buttons)

# Не хочешь, не надо. Закрыть сессию
@dp.request_handler(commands=['нет', 'не хочу'])
async def handle_user_stop(alice_request):
    track_message(m.user_id, m.session_id, 'no', m.command, False)
    return alice_request.response("Жаль, возвращайтесь как решите сыграть.\n"
                                  "До встречи!",
                                  end_session=True)


#Начинаем игру
@dp.request_handler(commands=['давай', 'начать игру', 'да', 'хочу'])
async def handle_user_agrees(alice_request):
    m = Message.create(alice_request)
    track_message(m.user_id, m.session_id, 'start_game', m.command, False)
    words = get_words()
    words_list = []
    for i in words:
        words_list.append(i["word"])
    shuffle(words_list)

    words_iter = iter(words_list)
    await dp.storage.update_data(m.user_id, words=words_iter)

    word = next(words_iter)
    exp = next(item for item in words if item["word"] == word)
    e1 = exp[e1]
    e2 = exp[e2]
    e3 = exp[e3]

    await dp.storage.update_data(user_id, answer=exp[a])
    await dp.storage.update_data(user_id, right_answers=0)
    await dp.storage.update_data(user_id, wrong_answers=0)

    return alice_request.response(
        f'Я назову слово и перечислю определения,'
        f' а вы должны выбрать один из вариантов и назвать его номер.\n'
        f'Всего будет пять слов.\n'
        f'Для завершения игры скажите "конец игры".\n\n'
        f'{word} - это:\n\n'
        f'1. {e1}\n'
        f'2. {e2}\n'
        f'3. {e3}\n',
        tts='Я назову слово - и - перечислю определения'
        f' а вы должны выбрать один из вариантов и назвать его номер - .\n'
        f'Всего будет пять слов. - \n'
        f'Для завершения игр+ы скажите - "конец игр+ы" -.\n\n'
        f'{word} - это:\n\n - '
        f'1. - {e1}\n - '
        f'2. - {e1}\n - '
        f'3. - {e1}\n - ',
        buttons=choose_buttons)


# Немного вариативности
@dp.request_handler(commands=['привет', 'как дела'])
async def handle_user_cancel(alice_request):
    return alice_request.response(
        "Так-то мы здесь поиграть собрались, а ну-ка давай начнем игру?",
        buttons=start_buttons)

@dp.request_handler(commands=['помощь', 'что ты умеешь', 'что ты умеешь?'])
async def handle_user_cancel(alice_request):
    m = Message.create(alice_request)
    track_message(m.user_id, m.session_id, 'help', m.command, False)
    return alice_request.response(
        "Я знаю много редких слов. Могу загадать тебе несколько. Хочешь попробовать?",
        buttons=start_buttons)

# Заканчиваем игру по команде
@dp.request_handler(commands=['конец игры'])
async def handle_user_cancel(alice_request):
    m = Message.create(alice_request)
    data = await dp.storage.get_data(m.user_id)
    right = data.get('right_answers')
    wrong = data.get('wrong_answers')
    return alice_request.response(
        f"Спасибо за игру!\n Правильных ответов: {right}\n"
        f"Неправильных ответов: {wrong}\n"
        f"До встречи!",
        tts='<speaker audio="alice-sounds-game-win-1.opus">'
        f"Спасибо за игру! - "
        f"Правильных ответов: {right}\n - "
        f"Неправильных ответов: {wrong}\n - "
        f"До встречи!",
        end_session=True, buttons=[REVIEW_BUTTON])


@dp.request_handler(commands=[
    "первый", "первый вариант", "один", "1",
    "второй", "второй вариант", "два", "2",
    "третий", "третий вариант", "три", "3"])
async def handle_user_answer(alice_request):
    m = Message.create(alice_request)
    track_message(m.user_id, m.session_id, 'choice', m.command, False)
    data = await dp.storage.get_data(m.user_id)
    words_iter = data.get('words')
    get_answer = int(data.get('answer')) - 1

    answer_list = ALL_ANSWERS[get_answer]
    if alice_request.request.command in answer_list:
        try:
            word = next(words_iter)
            exp = next(item for item in words if item["word"] == word)
            e1 = exp[e1]
            e2 = exp[e2]
            e3 = exp[e3]

            await dp.storage.update_data(m.user_id, answer=exp[a])
            right_answers = int(data.get('right_answers'))
            await dp.storage.update_data(m.user_id,
                                         right_answers=right_answers + 1)
            return alice_request.response(
                f'Верно!\n\n'
                f'Следующее слово.\n'
                f'{word} - это:\n\n'
                f'1. {e1}\n'
                f'2. {e2}\n'
                f'3. {e3}\n',
                tts='Верно!\n\n'
                f'Следующее слово.\n - '
                f'{word} - это:\n\n - '
                f'1. - {e1}\n - '
                f'2. - {e2}\n - '
                f'3. - {e3}\n - ',
                buttons=choose_buttons)
        except StopIteration:
            right = data.get('right_answers')
            wrong = data.get('wrong_answers')
            return alice_request.response(
                f"Вы ответили на все вопросы.\n"
                f"Спасибо за игру!\n"
                f"Правильных ответов: {right}\n"
                f"Неправильных ответов: {wrong}\n",
                tts='<speaker audio="alice-sounds-game-win-1.opus">'
                f"Вы ответили на все вопросы.\n - "
                f"Спасибо за игру!\n - "
                f"Правильных ответов: {right}\n - "
                f"Неправильных ответов: {wrong}\n - ",
                end_session=True, buttons=[REVIEW_BUTTON])
    else:
        wrong_answers = int(data.get('wrong_answers'))
        await dp.storage.update_data(m.user_id, wrong_answers=wrong_answers + 1)
        return alice_request.response('Неверно! Попробуйте еще раз.',
                                      buttons=choose_buttons)


# Все остальные запросы попадают сюда
@dp.request_handler()
async def handle_all_other_requests(alice_request):
    track_message(m.user_id, m.session_id, None, m.command, True)
    return alice_request.response(
        'Я не понимаю, твой запрос. Попробуй снова.'
        'Если хотите начать игру заново, скажите "начать игру"'
    )


if __name__ == '__main__':
    health = HealthCheck()
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    app.router.add_get("/healthz", health)
    app.router.add_get("/metrics", aio.web.server_stats)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)