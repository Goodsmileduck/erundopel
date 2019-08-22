from pymongo import MongoClient, monitoring
import os, logging
import csv

DB_HOST = 'localhost'
DB_PORT = 27017
DB_MAX_POOL_SIZE = 300
DB_NAME = 'erundopel'

class CommandLogger(monitoring.CommandListener):

    def started(self, event):
        logging.info("Command {0.command_name} with request id "
                     "{0.request_id} started on server "
                     "{0.connection_id}".format(event))

    def succeeded(self, event):
        logging.info("Command {0.command_name} with request id "
                     "{0.request_id} on server {0.connection_id} "
                     "succeeded in {0.duration_micros} "
                     "microseconds".format(event))

    def failed(self, event):
        logging.info("Command {0.command_name} with request id "
                     "{0.request_id} on server {0.connection_id} "
                     "failed in {0.duration_micros} "
                     "microseconds".format(event))

mongo = MongoClient(host=DB_HOST, port=DB_PORT, connect=True,
                    event_listeners=[CommandLogger()],
                    maxPoolSize=DB_MAX_POOL_SIZE)
db = mongo[DB_NAME]

with open("words.csv", "r", encoding="utf8") as csvfile:
    data = csv.DictReader(csvfile, delimiter=",", quotechar=" ")
    words = {x["word"]: [x["answer"],
             x["exp_1"], x['exp_2'],
             x['exp_3']] for x in data}


for word in words:
    print(word)
    db.words.insert_one({
        "word": word,
        "a": words[word][0],
        "e1": words[word][1],
        "e2": words[word][2],
        "e3": words[word][3]})