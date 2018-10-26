
import os, logging
import csv
from random import shuffle

from aiohttp import web
from aioalice import Dispatcher, get_new_configured_app, types
from aioalice.dispatcher import MemoryStorage, SkipHandler
from aioalice.utils.helper import Helper, HelperMode, Item

WEBHOOK_URL_PATH = '/'  # webhook endpoint
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 5000

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

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

with open("words.csv", "r", encoding="utf8") as csvfile:
    data = csv.DictReader(csvfile, delimiter=",", quotechar=" ")
    words = {x["word"]: [x["answer"],
             x["exp_1"], x['exp_2'],
             x['exp_3']] for x in data}


if LOG_LEVEL == logging.DEBUG:
    @dp.request_handler()
    async def take_all_requests(alice_request):
        # Логгируем запрос. Можно записывать в БД и тд
        logging.debug('New request! %r', alice_request)
        # Поднимаем исключение, по которому обработка перейдёт
        # к следующему хэндлеру, у которого подойдут фильтры
        raise SkipHandler

# Новая сессия. Приветствуем пользователя
@dp.request_handler(func=lambda areq: areq.session.new)
async def handle_new_session(alice_request):
    user_id = alice_request.session.user_id
    logging.info(f'Initialized new session!\nuser_id is {user_id!r}')

    return alice_request.response(
        "Привет! Ерундопель - это игра где нужно угадать "
        "правильное определение для слова. Хочешь попробовать?",
        tts="Привет! Ерундопель - это игра где нужно угадать "
        "правильное определение для сл+ова. Хочешь попробовать?",
        buttons=start_buttons)

# Не хочешь, не надо. Закрыть сессию
@dp.request_handler(commands=['нет', 'не хочу'])
async def handle_user_stop(alice_request):
    return alice_request.response("Жаль, возвращайтесь как решите сыграть.\n"
                                  "До встречи!",
                                  end_session=True)


#Начинаем игру
@dp.request_handler(commands=['давай', 'начать игру', 'да', 'хочу'])
async def handle_user_agrees(alice_request):
    user_id = alice_request.session.user_id
    words_list = list(words.keys())
    shuffle(words_list)
    words_iter = iter(words_list)
    await dp.storage.update_data(user_id, words=words_iter)

    word = next(words_iter)

    exp_1 = words[word][1]
    exp_2 = words[word][2]
    exp_3 = words[word][3]

    await dp.storage.update_data(user_id, answer=words[word][0])
    await dp.storage.update_data(user_id, right_answers=0)
    await dp.storage.update_data(user_id, wrong_answers=0)

    return alice_request.response(
        'Я буду говорить слова и определения,'
        ' а вы должны выбрать один из вариантов и назвать его номер.\n'
        'Для завершения игры скажите "конец игры".\n\n'
        '{word} - это:\n\n'
        '1. {exp_1}\n'
        '2. {exp_2}\n'
        '3. {exp_3}\n',
        tts='Я буду говорить слова и определения,'
        ' а вы должны выбрать один из вариантов и назвать его номер - .\n'
        'Для завершения игр+ы скажите - "конец игр+ы" -.\n\n'
        '{word} - это:\n\n'
        '1. {exp_1}\n'
        '2. {exp_2}\n'
        '3. {exp_3}\n',
        buttons=choose_buttons)


# Немного вариативности
@dp.request_handler(commands=['привет', 'как дела'])
async def handle_user_cancel(alice_request):
    return alice_request.response(
        "Так то мы здесь поиграть собрались, а ну-ка давай начем игру?",
        buttons=start_buttons)


# Заканчиваем игру по команде
@dp.request_handler(commands=['конец игры'])
async def handle_user_cancel(alice_request):
    user_id = alice_request.session.user_id
    data = await dp.storage.get_data(user_id)
    right = data.get('right_answers')
    wrong = data.get('wrong_answers')
    return alice_request.response(
        f"Спасибо за игру!\n Правильных ответов: {right}\n"
        f"Неправильных ответов: {wrong}\n"
        f"До встречи!",
        end_session=True)


@dp.request_handler(commands=[
    "первый", "первый вариант", "один", "1",
    "второй", "второй вариант", "два", "2",
    "третий", "третий вариант", "три", "3"])
async def handle_user_answer(alice_request):
    user_id = alice_request.session.user_id
    data = await dp.storage.get_data(user_id)
    words_iter = data.get('words')
    get_answer = int(data.get('answer')) - 1

    answer_list = ALL_ANSWERS[get_answer]
    if alice_request.request.command in answer_list:
        try:
            word = next(words_iter)

            exp_1 = words[word][1]
            exp_2 = words[word][2]
            exp_3 = words[word][3]

            await dp.storage.update_data(user_id, answer=words[word][0])
            right_answers = int(data.get('right_answers'))
            await dp.storage.update_data(user_id,
                                         right_answers=right_answers + 1)
            return alice_request.response(
                f'Верно!\n\n'
                f'Следующее слово.\n'
                f'{word} - это:\n\n'
                f'1. {exp_1}\n'
                f'2. {exp_2}\n'
                f'3. {exp_3}\n',
                buttons=choose_buttons)
        except StopIteration:
            right = data.get('right_answers')
            wrong = data.get('wrong_answers')
            return alice_request.response(
                f"Вы ответили на все вопросы.\n"
                f"Спасибо за игру!\n"
                f"Правильных ответов: {right}\n"
                f"Неправильных ответов: {wrong}\n",
                end_session=True)
    else:
        wrong_answers = int(data.get('wrong_answers'))
        await dp.storage.update_data(user_id, wrong_answers=wrong_answers + 1)
        return alice_request.response('Неверно! Попробуйте еще раз. ',
                                      buttons=choose_buttons)


# Все остальные запросы попадают сюда
@dp.request_handler()
async def handle_all_other_requests(alice_request):
    return alice_request.response(
        'Я не понимаю, твой запрос. Попробуй снова.'
        'Если хотите начать игру заново, скажите "начать игру"'
    )


if __name__ == '__main__':
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)