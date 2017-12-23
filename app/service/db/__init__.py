from app import settings
from pymongo import MongoClient

mongodb = None

# set MongoDB configuration
if settings.DATABASE_RECORD:
    if settings.DATABASE_SERVER_ADDRESS and settings.DATABASE_SERVER_PORT:
        mongo = MongoClient(settings.DATABASE_SERVER_ADDRESS, settings.DATABASE_SERVER_PORT)
        if settings.DATABASE_SERVER_USERNAME and settings.DATABASE_SERVER_PASSWORD:
            db_auth = mongo.admin
            db_auth.authenticate(settings.DATABASE_SERVER_USERNAME, settings.DATABASE_SERVER_PASSWORD)
        mongodb = eval("mongo." + settings.DATABASE_NAME)
