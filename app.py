import csv
from random import shuffle
from itertools import cycle


with open("words.csv", "r", encoding="utf8") as csvfile:
    data = csv.DictReader(csvfile, delimiter=",", quotechar=" ")
    words = {x["word"]: [x["answer"], x["exp_1"], x['exp_2'], x['exp_3']] for x in data}

nums = ['первый', 'второй', 'третий']
buttons = [{'title': str(n), 'hide': True} for n in nums]

# Функция для непосредственной обработки диалога.
def handle_dialog(request, response, user_storage):
    if request.is_new_session:
        user_storage = {}
        response.set_text('Привет! Ерундопель - это игра где нужно угадать правильное определение для слова. Хочешь попробовать?')
        response.set_buttons([{'title': 'Да', 'hide': True},
                              {'title': 'Нет', 'hide': True}])

        return response, user_storage

    else:
        # Обрабатываем ответ пользователя.
        if request.command.lower() == "конец игры":
            response.set_text("Спасибо за игру!\n Правильных ответов: {}\n".format(user_storage["right_answers"])
                              + "До встречи!")
            response.set_end_session(True)
            user_storage = {}

            return response, user_storage

        elif request.command.lower() in ['да', 'начнем', 'хочу']:
            _a = list(filter(lambda x: request.command.lower() == words[x][1], words.keys()))
            shuffle(_a)
            inf_list = cycle(_a)
            user_storage['questions'] = inf_list

            word = next(user_storage['questions'])
            answer = words[word][0]


            user_storage["word"] = word
            user_storage["answer"] = answer
            user_storage["buttons"] = buttons
            user_storage["right_answers"] = 0

            response.set_text('Я буду говорить слова и варианты объяснения, а ты должен выбрать один из вариантов.\n'
                              'Для завершения игры скажите "конец игры".\n'
                              '{} - это:\n'
                              '1. {}\n'
                              '2. {}\n'
                              '3. {}\n'.format(user_storage["word"],
                                               user_storage["exp_1"],
                                               user_storage["exp_2"],
                                               user_storage["exp_3"]))

            response.set_buttons(user_storage["buttons"])

            return response, user_storage

        elif request.command.lower() == user_storage["answer"]:
            # Пользователь ввел правильный вариант ответа.
            word = next(user_storage['questions'])
            answer = words[word][0]

            user_storage["word"] = word
            user_storage["answer"] = answer
            user_storage["buttons"] = buttons
            response.set_text('Верно!\n'
                              'Следующее слово.\n'
                              '{} - это:\n'.format(user_storage["word"])
                              '1. {}\n'.format(user_storage["exp_1"])
                              '2. {}\n'.format(user_storage["exp_2"])
                              '3. {}\n'.format(user_storage["exp_3"]))
            response.set_buttons(user_storage["buttons"])

            return response, user_storage

        response.set_text("Неверно! Попробуй еще раз.")

        return response, user_storage