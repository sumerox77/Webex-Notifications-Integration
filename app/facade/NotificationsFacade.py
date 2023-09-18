import logging

from application.service.NotificationCardsService import NotificationCardsService as Cards
from application.service.NotificationService import NotificationService as NotificationService


class NotificationsFacade:
    notificationService = None
    cards = None

    def __init__(self):
        self.notificationService = NotificationService()
        self.cards = Cards()

    def github_issue_handler(self, payload: dict, space_id: str):
        card = [self.cards.github_issue_card(
            title=payload["title"],
            reporter=payload["reporter"],
            labels=payload["labels"],
            html_url=payload["link_to"]
        )]

        self.notificationService.send_notification_to_space(space_id=space_id, attachments=card)

    def github_pull_request_handler(self, payload: dict, space_id: str):
        card = [self.cards.github_pr_card(
            pr_title=payload["title"],
            github_action="READY FOR REVIEW",
            html_url=payload["link"],
            project_name=payload["project_name"]
        )]

        message_id = self.notificationService.send_notification_to_space(
            space_id=space_id,
            attachments=card
        )

        self.notificationService.db_connector_messages.add_message(
            pull_request_id=payload["pull_request_id"],
            parent_message_id=message_id,
            email_to_notify=""
        )

    def github_pull_request_review_handler(self, payload: dict, space_id: str, state: str):
        pull_request_id = payload["pull_request_id"]

        if state in ["changes_requested"]:
            logging.info("Changes Requested!")
            child_message_ids = self.notificationService.db_connector_messages.get_child_message_array(
                pull_request_id=pull_request_id
            )
            for child_message_id in child_message_ids:
                self.notificationService.webex.messages.delete(child_message_id)

            self.notificationService.db_connector_messages.clear_child_message_array(pull_request_id=pull_request_id)
            logging.info(payload["review_requested_by"])

            email_to_notify = self.notificationService.db_connector_users.get_user_email(payload["review_requested_by"])
            logging.info(f"EMAIL::: {email_to_notify}")

            if self.__email_to_notify__(email_to_notify=email_to_notify, payload=payload):
                return {"message": f"User with email {email_to_notify} was notified!"}
            else:
                return {"message": f"User mapping for {payload['review_requested_by']} was not found!"}

        if state in ["approved"]:
            card = [self.cards.github_pr_review_card_approved(
                title=payload["title"],
                reviewed_by=payload["reviewed_by"],
                html_url=payload["reviewed_by_url"]
            )]

            parent_message_id = self.notificationService.db_connector_messages.get_parent_message(
                pull_request_id=pull_request_id
            )

            message_id = self.notificationService.send_notification_to_space(
                space_id=space_id,
                attachments=card,
                parent_id=parent_message_id
            )

            self.notificationService.db_connector_messages.update_message(
                pull_request_id=pull_request_id,
                child_message_id=message_id
            )
            email_to_notify = self.notificationService.db_connector_users.get_user_email(payload["review_requested_by"])
            if self.notificationService.db_connector_messages.is_pr_ready_for_review(pull_request_id=pull_request_id):
                self.__email_to_notify__(email_to_notify=email_to_notify, payload=payload)
                return {"message": f"User with email {email_to_notify} was notified!"}
            else:
                return {"message": f"User mapping for {payload['review_requested_by']} was not found!"}

    def circle_ci_handler(self, payload: dict, ):
        card = [self.cards.circle_ci_card(
            m_title=payload["subject_key"],
            branch_name=payload["github_branch_name"],
            status=payload["workflow_status_key"],
            github_url=payload["github_url_key"],
            circle_ci_url=payload["workflow_url_ci"],
            repo_name=payload["project_name"]
        )]

        self.notificationService.send_notification_to_user(email_list=[payload["to_user_email"]], attachments=card)

    def __email_to_notify__(self, email_to_notify, payload: dict):
        """This method checks if there's a mapping between github username and cisco email."""
        if email_to_notify:
            card_changes_requested = [self.cards.github_pr_review_card_changes_requested(
                title=payload['title'],
                github_pr_link=payload['github_pr_link'],
                reviewed_by=payload['reviewed_by'],
                reviewer_link=payload['reviewed_by_url']
            )]
            self.notificationService.send_notification_to_user(email_list=[email_to_notify],
                                                               attachments=card_changes_requested)
            logging.info(f"User with email {email_to_notify} was notified!")
            return True
        else:
            logging.info(f"User mapping for {payload['review_requested_by']} was not found!")
            return False

    def get_email_by_github_username(self, github_username: str):
        found_email = self.notificationService.db_connector_users.get_user_email(github_username)
        if found_email:
            return dict(status=200, github_username=github_username, found_email=found_email,
                        message=f"The username: {github_username} is mapped to {found_email}.")
        else:
            return dict(status=404, message=f"Mapping for {github_username} not found.")

    def add_email_mapping_to_github_username(self, github_username: str, cisco_email: str):
        logging.info(f"CISCO_EMAIL: {cisco_email}")
        if "@cisco.com" not in cisco_email:
            return dict(status=400, message=f"Email {cisco_email} is not in @cisco.com domain!")
        else:
            logging.info(f"if 1")

            card = [self.cards.welcome_message_card(
                github_username=github_username,
                cisco_email=cisco_email
            )]

            messageId = self.notificationService.send_notification_to_user(
                email_list=[cisco_email],
                attachments=card)
            if messageId is not None and len(messageId) > 0:

                self.notificationService.db_connector_users.add_or_update_user_mapping(
                    user_github_username=github_username,
                    user_github_cisco_email=cisco_email
                )
            return {
                "status": 200,
                "github_username": github_username,
                "found_email": cisco_email,
                "message": f"The username: {github_username} is mapped to {cisco_email}."}
