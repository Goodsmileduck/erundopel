from models import PhraseType, Phrase


def seed_phrases():
    Phrase(PhraseType.YOU_ARE_RIGHT.value, 'Угадал!').save()
    Phrase(PhraseType.YOU_ARE_RIGHT.value, 'Именно так. Мои нейроны восстанавливаются!').save()
    Phrase(PhraseType.YOU_ARE_RIGHT.value, 'Определённо верный ответ!').save()
    Phrase(PhraseType.YOU_ARE_RIGHT.value, 'Тысяча нейронов. Это правильно!').save()
    Phrase(PhraseType.YOU_ARE_RIGHT.value, 'Дефрагментировано! Спасибо за верный ответ!').save()
    Phrase(PhraseType.YOU_ARE_RIGHT.value, 'Прекрасный ответ! Так и запишу!').save()
    Phrase(PhraseType.YOU_ARE_RIGHT.value, 'Отлично! Моя база данных наполняется!').save()
    Phrase(PhraseType.YOU_ARE_RIGHT.value, 'Верно, новая нейронная связь создана!').save()
    Phrase(PhraseType.YOU_ARE_RIGHT.value, 'Святые транзисторы, это верно.').save()

    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Не думаю что это верно.').save()
    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Не верно. Я не помню такого.').save()
    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Ответная реакция нейронов не обнаружена. Это неверно.').save()
    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Не припомню такого.').save()
    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Моя память сильно фрагментирована, но это неверный ответ.').save()
    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Не верно. Плохо обученная нейросеть не будет полезной. Нужно будет обязательно найти ответ.').save()
    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Вероятность этого предельно мала, ответ неверен.').save()
    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Линейное преобразование невозможно, нужен другой ответ.').save()
    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Отсутсвует взаимодействие с другими векторами, значит ответ неверный.').save()
    Phrase(PhraseType.YOU_ARE_WRONG.value, 'Хороший вариант, но не подходит.').save()

    # two %s are necessary! %points and %level :
    Phrase(PhraseType.GREETING.value, 'Привет! Рад видеть тебя снова.\nТы правильно ответил на %(number)i %(question)s и достиг уровня "%(level)s"!\nСыграем ещё?').save()
    Phrase(PhraseType.GREETING.value, 'Здравствуй! Давно не виделись.\nТы прошёл %(number)i %(question)s! Твой уровень - "%(level)s"!\nНачнём игру?').save()
    Phrase(PhraseType.GREETING.value, 'Ох, сколько электронных эпох прошло! Давно не виделись.\nТы верно ответил на %(number)i %(question)s и достиг уровня "%(level)s"!\nИграем?').save()
    Phrase(PhraseType.GREETING.value, 'Рад что ты снова тут.\nУ тебя пройдено %(number)i %(question)s! Твой уровень - "%(level)s"!\nИграем?').save()
    Phrase(PhraseType.GREETING.value, 'Я рад что ты снова тут.\nУ тебя пройдено %(number)i %(question)s! Твой уровень - "%(level)s"!\nИграем?').save()

    Phrase(PhraseType.CONTINUE_ASK.value, 'Продолжим?').save()
    Phrase(PhraseType.CONTINUE_ASK.value, 'Идём дальше?').save()
    Phrase(PhraseType.CONTINUE_ASK.value, 'Продолжаем?').save()
    Phrase(PhraseType.CONTINUE_ASK.value, 'Хочешь продолжить?').save()
    Phrase(PhraseType.CONTINUE_ASK.value, 'Теперь продолжим?').save()

    Phrase(PhraseType.NEXT_QUESTION.value, 'Следующий вопрос.').save()
    Phrase(PhraseType.NEXT_QUESTION.value, 'Перейдём к следующему вопросу.').save()
    Phrase(PhraseType.NEXT_QUESTION.value, 'Я нашел еще фрагмент памяти.').save()
    Phrase(PhraseType.NEXT_QUESTION.value, 'А вот и еще вопрос.').save()
    Phrase(PhraseType.NEXT_QUESTION.value, 'Переходим в следующий слой нейросети. Нашел вопрос.').save()
    Phrase(PhraseType.NEXT_QUESTION.value, 'Где-то тут потерялся нейрон. Значит вот тебе вопрос.').save()
    Phrase(PhraseType.NEXT_QUESTION.value, 'Итак, новый вопрос.').save()
    Phrase(PhraseType.NEXT_QUESTION.value, 'Новый вопрос звучит так: ').save()

    # two %s are necessary! %points and %level :
    Phrase(PhraseType.NEW_LEVEL_CONGRATULATION.value, 'Поздравляю, даны ответы уже на %(number)i %(question)s и достигнут уровень "%(level)s"! Продолжай в том же духе!\nХочешь продолжить?').save()
    Phrase(PhraseType.NEW_LEVEL_CONGRATULATION.value, 'Невероятно! Ты прошёл уже %(number)i %(question)s, Твой новый уровень - "%(level)s"!\nИдём дальше?').save()

    Phrase(PhraseType.TRY_AGAIN.value, 'Попробуй ещё раз.').save()
    Phrase(PhraseType.TRY_AGAIN.value, 'Попытайся снова.').save()
    Phrase(PhraseType.TRY_AGAIN.value, 'Нужно попробовать еще.').save()
    Phrase(PhraseType.TRY_AGAIN.value, 'Давай еще попытку.').save()
    Phrase(PhraseType.TRY_AGAIN.value, 'Надо попробовать еще.').save()

    Phrase(PhraseType.FALLBACK_GENERAL.value, 'Прости, я, наверное, тебя не расслышал. Повтори, пожалуйста.').save()
    Phrase(PhraseType.FALLBACK_GENERAL.value, 'Я не понял, пожалуйста, попробуй перефразировать.').save()
    Phrase(PhraseType.FALLBACK_GENERAL.value, 'Моя нейросеть не смогла идентифицировать твой ответ. Попробуй повторить').save()
    Phrase(PhraseType.FALLBACK_GENERAL.value, 'Не могу расшифровать твой ответ, можешь перефразировать?').save()

    Phrase(PhraseType.FALLBACK_EXIT.value, 'Наверное, я сегодня не в форме. Заходи в другой раз.').save()

    Phrase(PhraseType.FALLBACK_2_BEGIN.value, 'Я потерял огромную часть словаря и иногда не понимаю простую человеческую речь.').save()
    Phrase(PhraseType.FALLBACK_2_BEGIN.value, 'Мои нейроны сильно повреждены и я забываю некоторые самые простые слова.').save()
    Phrase(PhraseType.FALLBACK_2_BEGIN.value, 'Мой словарь повреждён и я не всегда понимаю, что ты говоришь.').save()
    Phrase(PhraseType.FALLBACK_2_BEGIN.value, 'Я потерял очень много нейронов и не всегда понимаю, что ты имеешь в виду.').save()
    Phrase(PhraseType.FALLBACK_2_BEGIN.value, 'Моя память очень фрагментированна и я могу не помнить значения некоторых слов.').save()
    Phrase(PhraseType.FALLBACK_2_BEGIN.value, 'Моя память сильно пострадала при пожаре, и я не понимаю, что ты имеешь в виду.').save()
    Phrase(PhraseType.FALLBACK_2_BEGIN.value, 'Я много чего не помню и не всегда понимаю, что ты говоришь.').save()
    Phrase(PhraseType.FALLBACK_2_BEGIN.value, 'Некоторые слова пропали из моего словаря, иногда я не понимаю простую человеческую речь.').save()

    Phrase(PhraseType.LETS_PLAY.value, 'Давай играть!').save()
    Phrase(PhraseType.LETS_PLAY.value, 'Начинаем игру!').save()
    Phrase(PhraseType.LETS_PLAY.value, 'Начнём!').save()
    Phrase(PhraseType.LETS_PLAY.value, 'Отлично, давай начинать!').save()
    Phrase(PhraseType.LETS_PLAY.value, 'Хорошо, приступим!').save()
