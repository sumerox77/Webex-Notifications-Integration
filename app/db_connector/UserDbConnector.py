from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import logging


class MongoDbUserRepository:
    def __init__(self, login, password):
        uri = "mongodb://127.0.0.1:27017"
        client = MongoClient(uri, server_api=ServerApi('1'))
        try:
            client.admin.command('ping')
            logging.info("Pinged the deployment. Successfully connected to MongoDB!")
        except Exception as exception:
            logging.critical(f"Could not establish connection, {exception}")

        self.collection = client.webex_data.user_mapping

    def add_or_update_user_mapping(self, user_github_username, user_github_cisco_email):
        """Add/Update nickname mapping for webex notifications
        Args:
            :param: user_github_username user id from GitHub
            :param: user_github_cisco_email user email with @cisco.com domain,
        """
        logging.info('Calling add_or_update_user_mapping function')

        existing_mapping = self.collection.find_one({"user_github_id": user_github_username})

        if not existing_mapping:
            # Add a new message with 'pr_reviews' set to 0
            userMapping = {
                "user_github_id": user_github_username,
                "user_github_cisco_email": user_github_cisco_email
            }

            logging.info(f'Mapping new user with email: {userMapping}')
            insertedDocument = self.collection.insert_one(userMapping)
            logging.info(f'Mapped new user: {insertedDocument}')
            return True
        else:
            self.collection.update_one({"user_github_id": user_github_username},
                                       {
                                           "$set": {"user_github_cisco_email": user_github_cisco_email},
                                       })
            logging.info(f'Updated mapping for username{user_github_username}')
            return True

    def get_user_email(self, user_github_id):
        """Get user_email by user_github_username from payload.
        Args:
            user_github_username(str): GitHub username from payload
        """
        logging.info('Calling get_user_email_by_github_username function')
        user_email = self.collection.find_one({"user_github_id": user_github_id})
        logging.info(user_email)

        if user_email:
            logging.info(user_email['user_github_cisco_email'])
            return user_email['user_github_cisco_email']
