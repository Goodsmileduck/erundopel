import logging
from settings import DB_HOST, DB_PORT, DB_NAME, DB_MAX_POOL_SIZE
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, monitoring


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

#mongo_client = AsyncIOMotorClient(DB_HOST,
#                                  DB_PORT,
#                                  event_listeners=[CommandLogger()],
#                                  maxPoolSize=DB_MAX_POOL_SIZE)
#db = mongo_client[DB_NAME]
db = mongo[DB_NAME]