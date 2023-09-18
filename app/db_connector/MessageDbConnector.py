from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import logging


class MongoDbMessageRepository:
    def __init__(self, login, password):
        # Create a new client and connect to the server
        uri = "mongodb://127.0.0.1:27017"

        client = MongoClient(uri, server_api=ServerApi('1'))
        try:
            client.admin.command('ping')
            logging.info("Pinged the deployment. Successfully connected to MongoDB!")
        except Exception as exception:
            logging.critical(f"Could not establish connection, {exception}")

        self.collection = client.webex_data.message

    def add_message(self, pull_request_id: int, parent_message_id: str, email_to_notify: str = ""):
        """Add data about pull_request from payload when pull request is opened/reopened/ready_for_review.
        Args:
            pull_request_id(int): Pull request number from payload,
            parent_message_id(str): parent_message_id,
            email_to_notify(str): email_to_notify.
        """
        logging.info('Calling add_message function')
        existing_message = self.collection.find_one({"pull_request_id": pull_request_id})

        if not existing_message:
            # Add a new message with 'pr_reviews' set to 0
            new_message = {
                "parent_message_id": parent_message_id, "pr_reviews": 0, "email_to_notify": email_to_notify,
                "pull_request_id": pull_request_id, "child_message_array": []
            }
            logging.info(f'Inserting new message: {new_message}')
            insertedDocument = self.collection.insert_one(new_message)
            logging.info(f'Inserted new message: {insertedDocument}')

    def update_message(self, pull_request_id, child_message_id):
        """When PR approved, increment pr_reviews by 1. add child_message_id to array "approved_msg_id".
        Args:
            pull_request_id(int): Pull request number from payload,
            child_message_id(str): child_message_id to add to an array of approved_msg_id

        """
        logging.info('Calling update_message function')

        existing_message = self.get_message_by_pull_request_id(pull_request_id)
        if existing_message:
            self.collection.update_one({"pull_request_id": pull_request_id},
                                       {"$push": {"child_message_array": child_message_id}, "$inc": {"pr_reviews": 1}})
            logging.info(f'Updated message with pull_request_id {pull_request_id}')

    def get_message_by_pull_request_id(self, pull_request_id):
        """Get message by pull_request_id from payload.
        Args:
            pull_request_id(int): Pull request number from payload,
        """
        logging.info('Calling get_message_by_pull_request_id function')

        return self.collection.find_one({"pull_request_id": pull_request_id})

    def get_child_message_array(self, pull_request_id: int):
        """Returns an array of child message ids.
        Args:
            pull_request_id(int): Pull request number from payload
        """
        logging.info(f'Calling get_child_message_array function')

        return self.get_message_by_pull_request_id(pull_request_id)['child_message_array']

    def get_parent_message(self, pull_request_id: int):
        """Returns an array of child message ids.
        Args:
            pull_request_id(int): Pull request number from payload
        """
        logging.info(f'Calling get_child_message_array function')

        return self.get_message_by_pull_request_id(pull_request_id)['parent_message_id']

    def is_pr_ready_for_review(self, pull_request_id: int):
        logging.info(f'Checking if Pull Request with id: {pull_request_id} is ready for review')
        return len(self.get_message_by_pull_request_id(pull_request_id)['child_message_array']) == 2

    def clear_child_message_array(self, pull_request_id):
        """Set array of child messages to None, and pr_reviews counter to 0.
        This method is called when Pull Request payload action is "requested changes".
        Args:
            pull_request_id(int): Pull request number from payload
        """

        logging.info(f'Calling clear_child_message_array function')
        logging.info(f'Truncated child_message_array, pr_reviews is set to 0.')
        self.collection.update_one({"pull_request_id": pull_request_id},
                                   {"$set": {"child_message_array": [], "pr_reviews": 0}})
