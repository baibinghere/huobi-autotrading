from app import settings
from pymongo import MongoClient
from app.service.mailagent import MailAgent

mongodb = None
ma = None

# set MongoDB configuration
if settings.DATABASE_RECORD:
    if settings.DATABASE_SERVER_ADDRESS and settings.DATABASE_SERVER_PORT:
        mongo = MongoClient(settings.DATABASE_SERVER_ADDRESS, settings.DATABASE_SERVER_PORT)
        if settings.DATABASE_SERVER_USERNAME and settings.DATABASE_SERVER_PASSWORD:
            db_auth = mongo.admin
            db_auth.authenticate(settings.DATABASE_SERVER_USERNAME, settings.DATABASE_SERVER_PASSWORD)
        mongodb = eval("mongo." + settings.DATABASE_NAME)

# set MailAgent configuration
if settings.MAIL_ACCOUNT and settings.MAIL_AUTH_CODE and len(settings.MAIL_RECEIPIENTS) > 0:
    ma = MailAgent(settings.MAIL_ACCOUNT, settings.MAIL_AUTH_CODE)
