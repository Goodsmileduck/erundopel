from pymodm import MongoModel, fields, connect
import settings, random
from enum import Enum, unique


# Establish a connection to the database.
connect('mongodb://' + settings.DB_HOST + ':' + str(settings.DB_PORT) + '/' + settings.DB_NAME)



class Question(MongoModel):
    id = fields.IntegerField(primary_key=True)
    question = fields.CharField(max_length=2048)
    tts = fields.CharField(max_length=2048, blank=True)

    right_answers = fields.EmbeddedDocumentListField('Answer')
    possible_answers = fields.EmbeddedDocumentListField('Answer', blank=True)
    possible_answers_tts = fields.EmbeddedDocumentListField('Answer', blank=True)

    def __str__(self):
        return self.question


class Answer(MongoModel):
    answer = fields.CharField(max_length=512)

    def __str__(self):
        return self.answer


@unique
class PhraseType(Enum):
    YOU_ARE_RIGHT = 1
    YOU_ARE_WRONG = 2
    GREETING = 3
    CONTINUE_ASK = 4
    NEXT_QUESTION = 5
    TRY_AGAIN = 6
    FALLBACK_GENERAL = 7
    FALLBACK_EXIT = 8
    FALLBACK_2_BEGIN = 9
    LETS_PLAY = 10


class Phrase(MongoModel):
    PHRASE_TYPES = [a.value for a in PhraseType]
    phrase_type = fields.IntegerField(choices=PHRASE_TYPES)
    phrase = fields.CharField(max_length=2048)

    def __str__(self):
        return self.phrase_type + ' - ' + self.phrase

    @staticmethod
    def random_phrase(phrase_type):
        if isinstance(phrase_type, PhraseType):
            phrase_type = phrase_type.value
        return random.choice(list(Phrase.objects.raw({'phrase_type': phrase_type}))).phrase

    @staticmethod
    def give_you_are_right():
        return Phrase.random_phrase(PhraseType.YOU_ARE_RIGHT)

    @staticmethod
    def give_you_are_wrong():
        return Phrase.random_phrase(PhraseType.YOU_ARE_WRONG)

    @staticmethod
    def give_greeting():
        return Phrase.random_phrase(PhraseType.GREETING)

    @staticmethod
    def give_continue_ask():
        return Phrase.random_phrase(PhraseType.CONTINUE_ASK)

    @staticmethod
    def give_next_question():
        return Phrase.random_phrase(PhraseType.NEXT_QUESTION)

    @staticmethod
    def give_try_again():
        return Phrase.random_phrase(PhraseType.TRY_AGAIN)

    @staticmethod
    def give_fallback_general():
        return Phrase.random_phrase(PhraseType.FALLBACK_GENERAL)

    @staticmethod
    def give_fallback_exit():
        return Phrase.random_phrase(PhraseType.FALLBACK_EXIT)

    @staticmethod
    def give_fallback_2_begin():
        return Phrase.random_phrase(PhraseType.FALLBACK_2_BEGIN)

    @staticmethod
    def give_lets_play():
        return Phrase.random_phrase(PhraseType.LETS_PLAY)


class User(MongoModel):
    application_id = fields.CharField(max_length=128)
    state = fields.CharField(max_length=128)
    last_question = fields.ReferenceField(Question)

    def points(self):
        points = UserQuestion.objects.raw({'user': self._id, 'passed': True}).count()
        return points


class UserQuestion(MongoModel):
    user = fields.ReferenceField(User)
    question = fields.ReferenceField(Question)
    passed = fields.BooleanField()



