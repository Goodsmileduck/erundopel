import models, random


def test():
    print('\n\n\nTEST\n')
    # user = models.User(application_id='A9A8E1CB150550B27DEECBD766B436D6B098C96E9768BFE7F9C58A96DB437886', difficulty=1).save()

    # user = models.User.objects.raw({'application_id': 'A9A8E1CB150550B27DEECBD766B436D6B098C96E9768BFE7F9C58A96DB437886'}).first()
    # user_question = models.UserQuestion.objects.raw({'user':user._id}).delete()
    # user.delete()

    # raw_query = {'difficulty': {'$in': [1, 2, 3]}}
    # for question in models.Question.objects.raw(raw_query):
    #     models.UserQuestion(user=user._id, question=question.id, passed=bool(random.getrandbits(1))).save()
    #
    # print(user.gained_new_level())
    #
    # print(models.Phrase.give_you_are_right())

    print('\nEND TEST\n\n\n')
