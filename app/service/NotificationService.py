import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from application.db_connector.MessageDbConnector import MongoDbMessageRepository
from application.db_connector.UserDbConnector import MongoDbUserRepository
from webexteamssdk import WebexTeamsAPI
from webexteamssdk.models.immutable import Message as WebexMessageModel

logging.basicConfig(level=logging.INFO)


def __is_not_none__(object):
    return object is not None


class NotificationService:
    webex = None
    db_connector_messages = None
    db_connector_users = None

    def __init__(self):
        """Get credentials from .env for Webex Bot, and MongoDB"""
        logging.info(f"Environment variables from .env has been loaded = {load_dotenv(dotenv_path=Path('.env'))}")
        bot_token = os.getenv('BOT_TOKEN')
        mongo_db_login = os.getenv('MONGO_USERNAME')
        mongo_db_password = os.getenv('MONGO_PASSWORD')

        if __is_not_none__(bot_token):
            logging.info("STARTED: Webex Bot Initialization")
            self.webex = WebexTeamsAPI(access_token=bot_token)
            logging.info("FINISHED: Webex Bot Initialization")
        else:
            exit(1)

        if __is_not_none__(mongo_db_login) and __is_not_none__(mongo_db_password):
            logging.info("STARTED: Database Connection Initialization")
            self.db_connector_messages = MongoDbMessageRepository(login=mongo_db_login, password=mongo_db_password)
            logging.info("FINISHED: Database Connection Initialization")
        else:
            exit(1)

        if __is_not_none__(mongo_db_login) and __is_not_none__(mongo_db_password):
            logging.info("STARTED: Database Connection Initialization")
            self.db_connector_users = MongoDbUserRepository(login=mongo_db_login, password=mongo_db_password)
            logging.info("FINISHED: Database Connection Initialization")
        else:
            exit(1)

    def send_notification_to_user(self, email_list: list, attachments, default_message="", parent_id=""):
        deliveredMessagesListIds = []
        for email in email_list:
            logging.info(f"Sending Notification to: {email}")
            deliveredMessage: WebexMessageModel = self.webex.messages.create(
                toPersonEmail=email,
                parentId=parent_id,
                text=default_message,
                attachments=attachments)
            deliveredMessagesListIds.append(deliveredMessage.id)
        return deliveredMessagesListIds

    def send_notification_to_space(self, space_id, attachments, default_message: str = "default message", parent_id=""):
        """This method sends notification (adaptive card) to the space and return id of sent message."""
        deliveredMessage: WebexMessageModel = self.webex.messages.create(
            roomId=space_id,
            text=default_message,
            parentId=parent_id,
            attachments=attachments
        )
        return deliveredMessage.id
