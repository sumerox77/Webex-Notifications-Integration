import unittest
from unittest.mock import patch
from application.service.NotificationService import NotificationService
from application.service.NotificationCardsService import NotificationCardsService

ISSUES_SPACE_ID = "<>"


@patch.dict('os.environ', {
    'BOT_TOKEN':
        '<>>',
    "MONGO_USERNAME":
        "da",
    "MONGO_PASSWORD":
        "da",
})
@patch('application.service.NotificationService', spec=True)
@patch('application.service.NotificationCardsService', spec=True)
class TestNotificationService(unittest.TestCase):
    def test_init_with_valid_credentials(self, mock_notification_cards_service, mock_notification_service):
        instance = NotificationService()
        # Assertions
        self.assertIsNotNone(instance.webex)
        self.assertIsNotNone(instance.db_connector_messages)

    def test_send_message_issue(self, mock_notification_cards_service, mock_notification_service):
        notificationServiceInstance = NotificationService()
        notificationCardsService = NotificationCardsService()

        # Assertions
        self.assertIsNotNone(notificationServiceInstance.webex)
        self.assertIsNotNone(notificationServiceInstance.db_connector_messages)

        card = [notificationCardsService.github_issue_card(
            title="titleTest",
            reporter="reporterTest",
            html_url="https://google.com",
            labels="l1, l2, l3 Test"
        )]
        message_id = notificationServiceInstance.send_notification_to_space(space_id=ISSUES_SPACE_ID, attachments=card)

        self.assertIsNotNone(message_id)
        self.assertGreater(len(message_id), 0)

    def test_send_message_circle_ci_failed(self, mock_notification_cards_service, mock_notification_service):
        notificationServiceInstance = NotificationService()
        notificationCardsService = NotificationCardsService()

        # Assertions
        self.assertIsNotNone(notificationServiceInstance.webex)
        self.assertIsNotNone(notificationServiceInstance.db_connector_messages)

        card = [notificationCardsService.circle_ci_card(
            m_title="titleTest",
            branch_name="key_key_key_key",
            status="failed",
            github_url="https://google.com",
            circle_ci_url="https://google.com",
            repo_name="myrepo"
        )]

        message_id = notificationServiceInstance.send_notification_to_user(
            email_list=["atochyli@cisco.com"],
            attachments=card
        )

        self.assertIsNotNone(message_id)
        self.assertGreater(len(message_id), 0)

    def test_send_message_circle_ci_success(self, mock_notification_cards_service, mock_notification_service):
        notificationServiceInstance = NotificationService()
        notificationCardsService = NotificationCardsService()

        # Assertions
        self.assertIsNotNone(notificationServiceInstance.webex)
        self.assertIsNotNone(notificationServiceInstance.db_connector_messages)

        card = [notificationCardsService.circle_ci_card(
            m_title="titleTest",
            branch_name="key_key_key_key",
            status="success",
            github_url="https://google.com",
            circle_ci_url="https://google.com",
            repo_name="myrepo"
        )]

        message_id = notificationServiceInstance.send_notification_to_user(
            email_list=["atochyli@cisco.com"],
            attachments=card
        )

        self.assertIsNotNone(message_id)
        self.assertGreater(len(message_id), 0)

    def test_send_message_github_pr(self, mock_notification_cards_service, mock_notification_service):
        notificationServiceInstance = NotificationService()
        notificationCardsService = NotificationCardsService()

        # Assertions
        self.assertIsNotNone(notificationServiceInstance.webex)
        self.assertIsNotNone(notificationServiceInstance.db_connector_messages)

        card = [notificationCardsService.github_pr_card(
            pr_title="titleTest",
            github_action="READY_FOR_REVIEW",
            html_url="https://google.com",
            project_name="Test project name"
        )]

        message_id = notificationServiceInstance.send_notification_to_space(space_id=ISSUES_SPACE_ID, attachments=card)

        self.assertIsNotNone(message_id)
        self.assertGreater(len(message_id), 0)

    def test_send_message_github_pr_review(self, mock_notification_cards_service, mock_notification_service):
        notificationServiceInstance = NotificationService()
        notificationCardsService = NotificationCardsService()

        # Assertions
        self.assertIsNotNone(notificationServiceInstance.webex)
        self.assertIsNotNone(notificationServiceInstance.db_connector_messages)

        card_pr = [notificationCardsService.github_pr_card(
            pr_title="Test PR title",
            github_action="READY_FOR_REVIEW",
            html_url="https://google.com",
            project_name="Test project name"
        )]

        message_id = notificationServiceInstance.send_notification_to_space(space_id=ISSUES_SPACE_ID,
                                                                            attachments=card_pr)

        self.assertIsNotNone(message_id)
        self.assertGreater(len(message_id), 0)

        card_review = [notificationCardsService.github_pr_review_card_approved(
            title="title",
            reviewed_by="reviewer",
            html_url="https://google.com"
        )]

        message_id_review = notificationServiceInstance.send_notification_to_space(
            space_id=ISSUES_SPACE_ID,
            attachments=card_review,
            parent_id=message_id
        )

        self.assertIsNotNone(message_id_review)
        self.assertGreater(len(message_id_review), 0)


if __name__ == '__main__':
    unittest.main()
