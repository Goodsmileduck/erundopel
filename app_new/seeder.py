from models import Phrase, Question, Answer, User, UserQuestion, PhraseType
from pymongo import MongoClient
from settings import DB_HOST, DB_PORT, DB_NAME
import csv, os
import logging
from seed_phrases import seed_phrases

mongo_client = MongoClient(DB_HOST, DB_PORT).DB_NAME
db = mongo_client[DB_NAME]


def seed_questions_from_csv():
    # TODO get current file dir instead of current work dir
    with open("questions.csv", "r", encoding="utf-8-sig") as csvfile:
        data = csv.DictReader(csvfile, delimiter=";", quotechar='"')
        for q in data:
            # print(q['id'])
            right_answers = []
            possible_answers = []
            possible_answers_tts = []
            for x in q["right_answers"].split("|"):
                if x is not None and x != '':
                    right_answers.append(Answer(x.lower()))
            for x in q["possible_answers"].split("|"):
                if x is not None and x != '':
                    possible_answers.append(Answer(x))
            for x in q["possible_answers_tts"].split("|"):
                if x is not None and x != '':
                    possible_answers_tts.append(Answer(x.lower()))
            Question(
                id=q["id"],
                question_type=q["question_type"],
                question=q["question"],
                tts=q.get('tts', ''),
                clue=q["clue"],
                clue_tts=q["clue_tts"],
                difficulty=q["difficulty"],
                right_answers=right_answers,
                interesting_fact=q.get('interesting_fact', ''),
                interesting_fact_tts=q.get('interesting_fact_tts', ''),
                interesting_fact_pic_id=q.get('interesting_fact_pic_id', ''),
                possible_answers=possible_answers,
                possible_answers_tts=possible_answers_tts
            ).save()


def seed_questions():
    seed_questions_from_csv()


def test_seed():
    pass
    # user = User(application_id='1230-412').save()
    # question = Question.objects.all().first()
    # user_question = UserQuestion(user=user, question=question, passed=True).save()
    # print(user_question, user_question.user)
    # print(UserQuestion.objects.all().first())


def is_db_empty():
    return db.phrase.count_documents({}) == 0


def seed_all():
    # drop db before migration
    logging.info('Removing phrase collection')
    db.phrase.drop()
    logging.info('Removing question collection')
    db.question.drop()
    logging.info('Db was cleared')
    if is_db_empty():
        logging.info('Db is empty. Seeder started')
        seed_phrases()
        seed_questions()
        test_seed()
        logging.info('Seeder finished')
