import csv
from random import shuffle


with open("words.csv", "r", encoding="utf8") as csvfile:
    data = csv.DictReader(csvfile, delimiter=",", quotechar=" ")
    words = {x["word"]: [x["answer"], x["exp_1"], x['exp_2'], x['exp_3']] for x in data}

nums = ['первый', 'второй', 'третий', 'конец игры']
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
            response.set_text("Спасибо за игру!\n Правильных ответов: {}\n"
                              "Неправильных ответов: {}\n".format(user_storage["right_answers"], user_storage["wrong_answers"])
                              + "До встречи!")
            response.set_end_session(True)
            user_storage = {}

            return response, user_storage

        elif request.command.lower() in ['да', 'начнем', 'хочу']:
            _a = list(words.keys())
            shuffle(_a)
            user_storage['questions'] = _a

            word = next(user_storage['questions'])
            answer = words[word][0]

            user_storage["exp_1"] = words[word][1]
            user_storage["exp_2"] = words[word][2]
            user_storage["exp_3"] = words[word][3]

            user_storage["word"] = word
            user_storage["answer"] = answer
            user_storage["buttons"] = buttons
            user_storage["right_answers"] = 0
            user_storage["wrong_answers"] = 0

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
            try:
                word = next(user_storage['questions'])
                answer = words[word][0]

                user_storage["exp_1"] = words[word][1]
                user_storage["exp_2"] = words[word][2]
                user_storage["exp_3"] = words[word][3]

                user_storage["word"] = word
                user_storage["answer"] = answer
                user_storage["buttons"] = buttons
                user_storage["right_answers"] += 1
                response.set_text('Верно!\n'
                                  'Следующее слово.\n'
                                  '{} - это:\n'
                                  '1. {}\n'
                                  '2. {}\n'
                                  '3. {}\n'.format(user_storage["word"],
                                                   user_storage["exp_1"],
                                                   user_storage["exp_2"],
                                                   user_storage["exp_3"]))
                response.set_buttons(user_storage["buttons"])

                return response, user_storage
            except StopIteration:
                response.set_text("Вы ответили на все вопросы.\n Спасибо за игру!\n Правильных ответов: {}\n"
                                  "Неправильных ответов: {}\n".format(user_storage["right_answers"], user_storage["wrong_answers"])
                                  + "До встречи!")
                response.set_end_session(True)

        user_storage["wrong_answers"] += 1
        response.set_buttons(user_storage["buttons"])
        response.set_text("Неверно! Попробуй еще раз.")

        return response, user_storage