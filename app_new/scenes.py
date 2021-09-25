import enum
import inspect
import sys
from abc import ABC, abstractmethod
from typing import Optional

import intents
from request import Request
from response_helpers import (
    GEOLOCATION_ALLOWED,
    GEOLOCATION_REJECTED,
    button,
    has_location,
    image_gallery,
)
from state import STATE_RESPONSE_KEY, STATE_REQUEST_KEY
from settings import VERSION

from models import Phrase, Question, User, UserQuestion, PhraseType
import random
import logging, settings

from sounds import SoundFiles
import pymorphy2

morph = pymorphy2.MorphAnalyzer()


def search_in_session(request: Request, parameter):
    if request.state:
        param = request.state.get(STATE_REQUEST_KEY, {}).get(parameter, None)
        return param
    else:
        return None


def clear_not_passed_questions(user):
    not_passed_user_questions = UserQuestion.objects.raw({'user': user._id, 'passed': False})
    not_passed_user_questions.delete()


def give_random_question(request, user):
    all_user_questions = UserQuestion.objects.raw({'user': user._id})
    passed_questions_id = []
    for user_question in all_user_questions:
        passed_questions_id.append(user_question.question.id)
    logging.info(f"{request['session']['session_id']}: PASSED QUESTIONS - {passed_questions_id}")
    raw_query = {
        '_id': {'$nin': passed_questions_id},
    }
    questions = Question.objects.raw(raw_query)
    if not questions or questions.count() == 0:
        return None
    question = random.choice(list(questions))
    return question


def current_user(request):
    try:
        application_id = request['session'].get('application').get('application_id')
        user = User.objects.get({'application_id': application_id})
        return user
    except Exception as e:
        logging.debug(f"{request['session']['session_id']}: User does not exist. {e}")
        return None


def word_in_plural(word, number):
    return morph.parse(word)[0].make_agree_with_number(number).word


def clear_text(text):
    punctuation = ',./\\!?<>'
    for character in punctuation:
        text = text.replace(character, '')
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text.lower().strip()


def answer_is_right(request, question):
    try:
        user_reply = clear_text(request['request']['command'])
        right_answers = [answer.answer for answer in question.right_answers]
        if user_reply in right_answers:
            return True
        AVOID_WORDS = ('я', 'думаю', 'наверное', 'кажется', 'это', 'был', 'была', 'были', 'мне', 'конечно', 'разумеется'
                       'безусловно', )
        text_list = user_reply.split()
        user_reply = ' '.join([word for word in text_list if word not in AVOID_WORDS])
        # print(right_answers)
        return user_reply in right_answers or user_reply in settings.CHEATS
    except Exception as e:
        logging.error(f"{request['session']['session_id']}: ERROR looking of right answer. EXCEPTION:{e}" )
        return None


def handle_fallbacks(request, ReturnScene, **kwargs):
    # Catch fallbacks, needs a ReturnScene class, which has 'fallback' parameter
    fallback = search_in_session(request, 'fallback')
    if fallback:
        if fallback < 2:
            return ReturnScene(fallback=fallback+1, **kwargs)
        else:
            return Goodbye(fallback=1)
    return ReturnScene(fallback=1, **kwargs)


def give_fact_probability():
    # Returns if Interesting Fact should be given - True/False
    # n = random.randint(0, 10)
    # return n >= 7
    return True


class UserMeaning:
    def __init__(self, request):
        self.request = request
        self.user_request = self.request['request'].get('command', None)
        self.user_intents = self.request.intents

    def is_answer_in_match_answers(self, match_answers):
        cleaned = self.user_request.replace('пожалуйста', '')
        cleaned = clear_text(cleaned)
        return cleaned in match_answers

    def confirm(self):
        match_answers = ['да', 'конечно', 'пожалуй', 'да конечно', 'конечно да', 'давай', 'думаю да', 'хорошо',
                         'я готов', 'готов', 'да да', 'ага', 'идём', 'идем']
        return intents.YANDEX_CONFIRM in self.user_intents or self.is_answer_in_match_answers(match_answers)

    def do_continue(self):
        match_answers = ['давай продолжим', 'продолжим', 'продолжаем', 'хочу продолжить', 'давай продолжать',
                         'продолжай', 'давай продолжай', 'продолжи', 'продолжить', 'продолжать']
        return self.is_answer_in_match_answers(match_answers)

    def deny(self):
        match_answers = ['нет', 'не хочу', 'не надо', 'не думаю', 'наверное нет', 'конечно нет', 'не надо', 'нет нет']
        return intents.YANDEX_REJECT in self.user_intents or self.is_answer_in_match_answers(match_answers)

    def dont_know(self):
        match_answers = ['не знаю', 'я не знаю', 'не уверен', 'я не уверен', 'без понятия', 'даже не знаю']
        return self.is_answer_in_match_answers(match_answers)

    def lets_play(self):
        match_answers = ['давай играть', 'начнем', 'играем', 'сыграем', 'поехали', 'могу']
        return intents.START_QUIZ in self.user_intents or self.is_answer_in_match_answers(match_answers)

    def skip_question(self):
        match_answers = ['пропустить', 'пропусти вопрос', 'пропусти', 'следующий вопрос', 'следующий',
                         'давай следующий', 'дальше', 'далее', 'давай дальше']
        return self.is_answer_in_match_answers(match_answers)

    def repeat(self):
        match_answers = ['повтори', 'ещё раз', 'еще раз', 'скажи ещё раз', 'давай ещё раз', 'повторить',
                         'можешь повторить', 'повтори вопрос']
        return intents.YANDEX_REPEAT in self.user_intents or self.is_answer_in_match_answers(match_answers)

    def repeat_options(self):
        match_answers = ['повтори варианты', 'пожалуйста повтори варианты', 'скажи варинаты отвеов',
                         'повтори варианты ответов', 'повтори ответы', 'какие варианты', 'какие варианты ответов',
                         'какие варианты ответа', 'варианты ответа', 'повтори пожалуйста варианты',
                         'повтори пожалуйста варианты ответов', 'какие есть варианты']
        return intents.YANDEX_REPEAT in self.user_intents or self.is_answer_in_match_answers(match_answers)


class Scene(ABC):

    @classmethod
    def id(self):
        return self.__name__

    """Генерация ответа сцены"""
    @abstractmethod
    def reply(self, request):
        raise NotImplementedError()

    """Проверка перехода к новой сцене"""
    def move(self, request: Request):
        next_scene = self.handle_global_intents(request)
        if next_scene is None:
            next_scene = self.handle_local_intents(request)
        return next_scene

    @abstractmethod
    def handle_global_intents(self, request):
        raise NotImplementedError()

    @abstractmethod
    def handle_local_intents(self, request: Request) -> Optional[str]:
        raise NotImplementedError()

    def fallback(self, request: Request):
        return self.make_response('Извините, я вас не понимаю. Пожалуйста, попробуйте переформулировать вопрос.')

    def make_response(self, text, tts=None, card=None, state=None, buttons=None, directives=None):

        response = {
            'text': text,
            'tts': tts if tts is not None else text,
        }
        if card is not None:
            response['card'] = card
        if buttons is not None:
            response['buttons'] = buttons
        if directives is not None:
            response['directives'] = directives
        webhook_response = {
            'response': response,
            'version': '1.0',
            'application_state': {'version': VERSION },
            STATE_RESPONSE_KEY: {
                'scene': self.id(),
            },
        }
        if state is not None:
            webhook_response[STATE_RESPONSE_KEY].update(state)
        return webhook_response


class Main(Scene):
    def __init__(self, fallback=0):
        super(Main, self).__init__()
        self.fallback = fallback

    def handle_global_intents(self, request):
        user_meant = UserMeaning(request)
        if intents.YANDEX_HELP in request.intents:
            return GetHelp()
        elif intents.YANDEX_WHAT_CAN_YOU_DO in request.intents and intents.YANDEX_CONFIRM not in request.intents:
            return WhatCanYouDo()
        elif intents.EXIT in request.intents:
            return Goodbye()
        elif request['request']['command'] == "версия":
             return GetVersion()
        else:
            return None


class Welcome(Main):
    def reply(self, request: Request):
        sound_file_name = ''
        card = None

        if request['request']['command'] == "ping":
            response_pong = self.make_response("pong")
            return response_pong

        if self.fallback == 1:
            text = Phrase.give_fallback_general()
        elif self.fallback > 1:
            text = Phrase.give_fallback_2_begin() + ' Пожалуйста, ответь да или нет, - готов ли ты восстановить мне некоторые факты?'
        else:
            # User identification
            user = current_user(request)
            if user:
                first_time = False
                logging.info(f"User come back. application_id: {user.application_id} sessions: {request['session']['session_id']}")
                sound_file_name = SoundFiles.WELCOME_SECOND.value
            else:
                user = User(application_id=request['session'].get('application').get('application_id')).save()
                sound_file_name = SoundFiles.WELCOME_FIRST.value
                first_time = True
                logging.info(f"New user. application_id: {user.application_id} session: {request['session']['session_id']}")

            gained_new_level, level, points = user.gained_new_level()
            if first_time or points < 1:
                text = 'Привет! Ерундопель - это игра где нужно угадать ' \
                       'правильное определение редких слов.\n' \
                       'Хочешь попробовать?'
                tts='Привет! Ерундопель - это игра, где нужно угадать ' \
                    'правильное определение редких слов. - ' \
                    'Хочешь попробовать?'
            else:
                word = word_in_plural('вопрос', points)
                text = Phrase.give_greeting() % {'number': points,
                                                 'question': word,
                                                 'level': level}
            card = {
                'type': 'BigImage',
                'image_id': settings.WELCOME_IMAGE,
                'description': text,
            }

        response = self.make_response(
            text,
            tts=sound_file_name + text,
            buttons=[button('Давай играть', hide=True)],
            state={'fallback': self.fallback},
            card=card
        )
        return response

    def handle_local_intents(self, request: Request):
        user = current_user(request)

        user_meant = UserMeaning(request)

        if user_meant.lets_play() or user_meant.confirm():
            return AskQuestion(lets_play=True)
        elif user_meant.deny():
            return Goodbye()
        elif user_meant.repeat():
            return Welcome()

        return handle_fallbacks(request, Welcome)


class AskQuestion(Main):
    def __init__(self, give_confirmation=False, give_denial=False, repeat=False, repeat_options=False, lets_play=False):
        super(AskQuestion, self).__init__()
        self.give_confirmation = give_confirmation
        self.give_denial = give_denial
        self.wrong_answer = False
        self.repeat = repeat
        self.repeat_options = repeat_options
        self.lets_play = lets_play

    def reply(self, request: Request):
        user = current_user(request)
        tts = ''
        text = ''

        # Wrong answer, giving one more attempt
        if self.wrong_answer:
            attempts = search_in_session(request, 'attempts')
            if not attempts:
                attempts = 1
            question_id = search_in_session(request, 'question_id')
            question = Question.objects.get({'_id': question_id})
            text = Phrase.give_you_are_wrong() + '\n' + Phrase.give_try_again()
            state = {
                'question_id': question.id,
                'attempts': attempts+1,
            }
            self.wrong_answer = False
        # Asked for repeat question
        elif self.repeat:
            question_id = search_in_session(request, 'question_id')
            question = Question.objects.get({'_id': question_id})
            text = question.question
            if question.tts and question.tts != '':
                tts = question.tts
            else:
                tts = text
            state = {
                'question_id': question.id,
                'attempts': search_in_session(request, 'attempts'),
            }
        # Asked to repeat options
        elif self.repeat_options:
            question_id = search_in_session(request, 'question_id')
            question = Question.objects.get({'_id': question_id})
            text = question.question
            tts = '- '
            state = {
                'question_id': question.id,
                'attempts': search_in_session(request, 'attempts'),
            }
        # Give random question
        else:
            question = give_random_question(request=request, user=user)
            if not question:
                clear_not_passed_questions(user)
                question = give_random_question(request=request, user=user)
                if not question:
                    return self.make_response('Это просто невероятно, ты прошёл все вопросы! Поздравляю! \n'
                                              'Возвращайся чуть позже за новыми словами. \nСПАСИБО!!!')
            gained_level, level, points = user.gained_new_level()
            if self.lets_play:
                if points < 1:
                    text = tts = "Я смогу проверить только 2 ответа на каждый вопрос. У тебя всегда есть возможность пропустить или повторить вопрос.\nНачнём!\n"
                else:
                    text = tts = Phrase.give_lets_play() + '\n'
            else:
                next_question = Phrase.give_next_question()
                text += next_question + '\n'
                tts += next_question + ' - '
            text += question.question
            if question.tts and question.tts != '':
                tts += question.tts
            else:
                tts += question.question
            # Give random confirmation phrase if last answer was right
            if self.give_confirmation:
                confirmation = Phrase.give_you_are_right()
                text = confirmation + '\n' + text
                tts = confirmation + ' - ' + tts
            # Give random denial phrase if last answer was wrong
            elif self.give_denial:
                denial = Phrase.give_you_are_wrong()
                text = denial + '\n' + text
                tts = denial + ' - ' + tts
            state = {'question_id': question.id}
            self.give_denial = False

        if tts == '':
            tts = text
        # Add right answers to buttons
        buttons = []
        number_of_answers = len(question.possible_answers)
        for i, answer in enumerate(question.possible_answers):
            buttons.append(button(answer.answer, hide=True))
            if not question.possible_answers_tts:
                if i != number_of_answers - 1:
                    tts += ' - ' + answer.answer + ','
                else:
                    tts += ' - или ' + answer.answer + '?'
        if question.possible_answers_tts:
            number_of_answers_tts = len(question.possible_answers_tts)
            for i, answer_tts in enumerate(question.possible_answers_tts):
                if i != number_of_answers_tts - 1:
                    tts += ' - ' + answer_tts.answer + ','
                else:
                    tts += ' - или ' + answer_tts.answer + '?'
        buttons.append(button('Пропустить', hide=True))

        return self.make_response(text, state=state, buttons=buttons, tts=tts)

    def handle_local_intents(self, request: Request):
        user = current_user(request)
        user_meant = UserMeaning(request)
        question_id = search_in_session(request, 'question_id')
        question = Question.objects.get({'_id': question_id})
        logging.info(f"{request['session']['session_id']}: Question #{question_id} - {question}")

        # Check if response contains right answer
        if answer_is_right(request, question):
            UserQuestion(user=user, question=question_id, passed=True).save()
            return AskQuestion(give_confirmation=True)


        elif user_meant.skip_question() or user_meant.dont_know():
            if not search_in_session(request):
                return SkipQuestion()
            UserQuestion(user=user, question=question_id, passed=False).save()
            return AskQuestion()

        elif user_meant.repeat():
            return AskQuestion(repeat=True)

        # Assume answer as wrong
        attempts = search_in_session(request, 'attempts')
        if attempts and attempts >= settings.MAX_ATTEMPTS:
            UserQuestion(user=user, question=question_id, passed=False).save()
            return AskQuestion(give_denial=True)
        logging.warning(f"{request['session']['session_id']}: ATTEMPTS - {attempts}")
        self.wrong_answer = True
        return self


class SkipQuestion(Main):
    def reply(self, request: Request):
        if self.fallback == 1:
            text = Phrase.give_fallback_general()
        elif self.fallback > 1:
            text = Phrase.give_fallback_2_begin() + ' Пожалуйста, ответь да или нет, - дать подсказку??'
        attempts = search_in_session(request, 'attempts')
        if not attempts:
            attempts = 1
        state = {
            'question_id': search_in_session(request, 'question_id'),
            'attempts': attempts,
            'fallback': self.fallback,
        }
        return self.make_response(text, state=state, buttons=[
            button('Да', hide=True),
            button('нет', hide=True),
        ])

    def handle_local_intents(self, request: Request):
        user = current_user(request)
        question_id = search_in_session(request, 'question_id')
        user_meant = UserMeaning(request)
        if user_meant.confirm():
            return AskQuestion()
        elif user_meant.deny() or user_meant.skip_question():
            UserQuestion(user=user, question=question_id, passed=False).save()
            return AskQuestion()
        elif user_meant.repeat():
            return SkipQuestion()
        return handle_fallbacks(request, SkipQuestion)


class GetHelp(Main):
    def reply(self, request: Request):
        if self.fallback == 1:
            text = Phrase.give_fallback_general()
        elif self.fallback > 1:
            text = Phrase.give_fallback_2_begin() + ' Пожалуйста, ответь да или нет, -'
        else:
            text = 'Чтобы помочь мне восстановить данные для моих нейронов, ' \
            'Тебе нужно отвечать на мои вопросы. Есть два режима сложности - легкий и трудный. '\
            'Ты всегда можешь изменить уровень сложности. '\
            'Я также могу поискать подсказку в фрагментах памяти или '\
            'ты можешь пропустить вопрос если не знаешь ответа. '\

        if request.state is not None:
            attempts = search_in_session(request, 'attempts')
            question_id = search_in_session(request, 'question_id')
            state = {
                'question_id': question_id,
                'attempts': attempts,
                'fallback': self.fallback,
            }
            end_text = 'Продолжаем?'

            return self.make_response(text+end_text, state=state, buttons=[button('Да', hide=True)])
        else:
            end_text = 'Хочешь попробовать?'
            return self.make_response(text+end_text, buttons=[button('Да', hide=True)])

    def handle_local_intents(self, request: Request):
        user = current_user(request)
        user_meant = UserMeaning(request)
        user_intent = request.intents
        logging.info(f"{request['session']['session_id']}: User intent - {user_intent}")
        if user_meant.lets_play() or user_meant.confirm() or user_meant.do_continue():
            return AskQuestion(lets_play=True)
        elif user_meant.repeat():
            return GetHelp()
        return handle_fallbacks(request, GetHelp)


class GetVersion(Main):
    def reply(self, request: Request):
        if self.fallback == 1:
            text = Phrase.give_fallback_general()
        elif self.fallback > 1:
            text = Phrase.give_fallback_2_begin() + ' Пожалуйста, ответь да или нет, -'
        else:
            text = f'Версия нейросети {VERSION} . '

        if request.state is not None:
            attempts = search_in_session(request, 'attempts')
            question_id = search_in_session(request, 'question_id')
            state = {
                'question_id': question_id,
                'attempts': attempts,
                'fallback': self.fallback,
            }
            end_text = 'Продолжаем?'

            return self.make_response(text+end_text, state=state, buttons=[button('Да', hide=True)])
        else:
            end_text = 'Хочешь попробовать?'
            return self.make_response(text+end_text, buttons=[button('Да', hide=True)])

    def handle_local_intents(self, request: Request):
        user = current_user(request)
        user_meant = UserMeaning(request)
        user_intent = request.intents
        logging.info(f"{request['session']['session_id']}: User intent - {user_intent}")
        if user_meant.lets_play() or user_meant.confirm() or user_meant.do_continue():
            return AskQuestion(lets_play=True)
        elif user_meant.repeat():
            return GetVersion()
        return handle_fallbacks(request, GetVersion)


class WhatCanYouDo(Main):
    def reply(self, request: Request):
        if self.fallback == 1:
            text = Phrase.give_fallback_general()
        elif self.fallback > 1:
            text = Phrase.give_fallback_2_begin() + ' Пожалуйста, ответь да или нет, - хочешь сыграть?'
        else:
            text = "Я знаю много редких слов. Могу загадать тебе несколько. Хочешь попробовать?"
        return self.make_response(text, buttons=[
            button('Хочу', hide=True)],
            state={'fallback': self.fallback},
        )
    
    def handle_local_intents(self, request: Request):
        user = current_user(request)
        user_meant = UserMeaning(request)
        user_intent = request.intents
        logging.info(f"{request['session']['session_id']}: User intent - {user_intent}")
        if user_meant.lets_play() or user_meant.confirm() or user_meant.do_continue():
            return AskQuestion(lets_play=True)
        elif user_meant.repeat():
            return WhatCanYouDo()
        return handle_fallbacks(request, WhatCanYouDo)


class Goodbye(Main):
    def reply(self, request: Request):
        if self.fallback == 1:
            text = Phrase.give_fallback_exit()
        elif self.fallback > 1:
            text = Phrase.give_fallback_2_begin()
        else:
            text = 'Буду рад видеть тебя снова!'
        response = self.make_response(text, state={'fallback': self.fallback})
        if 'response' in response.keys():
            response['response']['end_session'] = True
        else:
            response['response'] = {'end_session': True}
        return response

    def handle_local_intents(self, request: Request):
        return handle_fallbacks(request, Goodbye)


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


SCENES = {
    scene.id(): scene for scene in _list_scenes()
}

DEFAULT_SCENE = Welcome
