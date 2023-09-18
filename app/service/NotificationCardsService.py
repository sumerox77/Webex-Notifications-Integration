from pyadaptivecards.actions import OpenUrl
from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.components import Column, Image
from pyadaptivecards.components import TextBlock
from pyadaptivecards.container import ColumnSet
from pyadaptivecards.options import Colors, ImageSize, FontSize, HorizontalAlignment
import logging


class NotificationCardsService:
    def __init__(self):
        ...

    def circle_ci_card(self, m_title: str, branch_name: str, status: str, github_url: str, circle_ci_url: str,
                       repo_name: str):
        logging.info("Creating CircleCI Adaptive card for Webex.")
        return self.__create_card_circle_ci__(
            m_title=m_title,
            branch_name=branch_name,
            status=status,
            github_url=github_url,
            circle_ci_url=circle_ci_url,
            repository_name=repo_name
        )

    def github_pr_card(self, pr_title: str, github_action: str, html_url: str, project_name: str):
        logging.info("Creating Github Pull Request Adaptive card for Webex.")
        return self.__create_card_github_pr__(
            pr_title=pr_title,
            github_action=github_action,
            html_url=html_url,
            project_name=project_name
        )

    def github_pr_review_card_approved(self, title: str, reviewed_by: str, html_url: str):
        logging.info("Creating Github Pull Review Request Adaptive card for Webex. (APPROVED)")
        return self.__create_card_github_review__(
            title=title,
            reviewed_by=reviewed_by,
            html_url=html_url
        )

    def github_pr_review_card_changes_requested(self, title: str, github_pr_link: str, reviewed_by: str,
                                                reviewer_link: str):
        logging.info("Creating Github Pull Review Request Adaptive card for Webex. (CHANGES REQUESTED)")
        return self.__create_card_github_review_changes_requested__(
            title=title,
            link_to_pr=github_pr_link,
            reviewed_by=reviewed_by,
            reviewer_link=reviewer_link
        )

    def github_issue_card(self, title: str, reporter: str, html_url: str, labels: str):
        logging.info("Creating Github Issue Adaptive card for Webex.")
        return self.__create_card_github_issue__(
            title=title,
            reporter=reporter,
            html_url=html_url,
            labels=labels
        )

    def welcome_message_card(self, github_username: str, cisco_email: str):
        logging.info("Creating Email Mapping Adaptive card for Webex.")
        return self.__welcome_message__(
            github_username=github_username,
            cisco_email=cisco_email
        )

    def __create_card_circle_ci__(self, m_title: str, branch_name: str, status: str, github_url: str,
                                  circle_ci_url: str,
                                  repository_name: str):
        # CircleCI Adaptive Card Builder
        project_title = TextBlock(f"**Commit Subject: '{m_title}'**", wrap=True, size=FontSize.MEDIUM, maxLines=3)

        happened_in_repo_branch = TextBlock(f"In repo/branch:", wrap=True, size=FontSize.MEDIUM, maxLines=3)
        repo_branch = TextBlock(f"'{repository_name}/{branch_name}'", wrap=True, size=FontSize.MEDIUM, maxLines=3)

        workflow_status = None
        if status == "failed":
            workflow_status = TextBlock(text=f"Build status: **{status.upper()}** ❌", color=Colors.ATTENTION)
        elif status == "success":
            workflow_status = TextBlock(text=f"Build status: **{status.upper()}** ✅", color=Colors.GOOD)

        open_url_github = OpenUrl(url=f"{github_url}/tree/{branch_name}", title="Open GitHub branch")
        open_url_circleci = OpenUrl(url=f"{circle_ci_url}", title="Open CircleCi workflow")

        circle_ci_img = Image(
            url="https://pbs.twimg.com/profile_images/1630994749929791491/ehhv739o_400x400.jpg",
            altText="CircleCI icon",
            size=ImageSize.SMALL,
            horizontalAlignment=HorizontalAlignment.RIGHT
        )

        column_main_info = Column(items=[project_title, happened_in_repo_branch, repo_branch], width=60)
        column_circle_ci_img = Column(items=[circle_ci_img])

        column_set_combination = ColumnSet([column_main_info, column_circle_ci_img])

        adaptive_card_with_data = AdaptiveCard(body=[column_set_combination, workflow_status],
                                               actions=[open_url_github, open_url_circleci])

        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": adaptive_card_with_data.to_dict()
        }

        return attachment

    def __create_card_github_pr__(self, pr_title: str, github_action: str, html_url: str, project_name: str):
        project_title = TextBlock(f"**In repo:** '{project_name}'", wrap=True, size=FontSize.MEDIUM, maxLines=3,
                                  horizontalAlignment=HorizontalAlignment.LEFT)
        pr_title = TextBlock(f"Title: '{pr_title}'", wrap=True, size=FontSize.MEDIUM, maxLines=3,
                             horizontalAlignment=HorizontalAlignment.LEFT)
        sub_title = TextBlock(f"**IS {github_action.upper()} ✅**", size=FontSize.MEDIUM, maxLines=1,
                              horizontalAlignment=HorizontalAlignment.LEFT, color=Colors.GOOD)
        open_url_github = OpenUrl(url=f"{html_url}", title="Review Pull Request")
        open_pr_files = OpenUrl(url=f"{html_url}/files", title="Review Changed Files")

        github_image = Image(
            url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            backgroundColor="#FFFFFF",
            altText="Github icon",
            size=ImageSize.SMALL,
            horizontalAlignment=HorizontalAlignment.RIGHT
        )

        column_main_info = Column(items=[project_title, pr_title, sub_title], width=40)
        column_image = Column(items=[github_image])

        column_set_combination = ColumnSet([column_main_info, column_image])

        adaptive_card_with_data = AdaptiveCard(body=[column_set_combination],
                                               actions=[open_url_github, open_pr_files])
        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": adaptive_card_with_data.to_dict()
        }

        return attachment

    def __create_card_github_issue__(self, title: str, reporter: str, html_url: str, labels: str):
        card_title = TextBlock(f"**Title:** '{title}'", wrap=True, size=FontSize.MEDIUM, maxLines=3,
                               horizontalAlignment=HorizontalAlignment.LEFT)
        card_reporter = TextBlock(f"Reported by: {reporter}", wrap=True, size=FontSize.MEDIUM, maxLines=3,
                                  horizontalAlignment=HorizontalAlignment.LEFT)
        card_labels = TextBlock(f"Labels: {labels}", size=FontSize.MEDIUM, maxLines=2,
                                horizontalAlignment=HorizontalAlignment.LEFT)
        open_url_issue = OpenUrl(url=f"{html_url}", title="Review issue")

        column_main_info = Column(items=[card_title, card_reporter, card_labels], width=40)
        column_set_combination = ColumnSet([column_main_info])

        adaptive_card_with_data = AdaptiveCard(body=[column_set_combination], actions=[open_url_issue])
        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": adaptive_card_with_data.to_dict()
        }

        return attachment

    def __create_card_github_review__(self, title: str, reviewed_by: str, html_url: str):
        # card_title = TextBlock(f"**Title:** '{title}'", wrap=True, size=FontSize.MEDIUM, maxLines=2,
        #                        horizontalAlignment=HorizontalAlignment.LEFT)
        card_reviewer = TextBlock(f"This PR was approved by:  [{reviewed_by}]({html_url}) ✅", wrap=True,
                                  size=FontSize.MEDIUM, maxLines=2,
                                  horizontalAlignment=HorizontalAlignment.LEFT)  # add link here

        column_main_info = Column(items=[card_reviewer], width=35)
        column_set_combination = ColumnSet([column_main_info])

        adaptive_card_with_data = AdaptiveCard(body=[column_set_combination])
        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": adaptive_card_with_data.to_dict()
        }

        return attachment

    def __create_card_github_review_changes_requested__(self, title: str, link_to_pr: str, reviewed_by: str,
                                                        reviewer_link: str):
        card_title = TextBlock(f"⚠️ Changes requested in: [{title}]({link_to_pr}) by [{reviewed_by}]({reviewer_link})",
                               wrap=True, size=FontSize.MEDIUM, maxLines=5,
                               horizontalAlignment=HorizontalAlignment.LEFT)

        column_main_info = Column(items=[card_title], width=35)
        column_set_combination = ColumnSet([column_main_info])

        adaptive_card_with_data = AdaptiveCard(body=[column_set_combination])
        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": adaptive_card_with_data.to_dict()
        }

        return attachment

    def __welcome_message__(self, github_username: str, cisco_email):
        card_title = TextBlock(
            f"Hi, {cisco_email.replace('@cisco.com', '')}, "
            f"the username {github_username} was successfully mapped with your cisco email:({cisco_email})",
            wrap=True, size=FontSize.MEDIUM, maxLines=5,
            horizontalAlignment=HorizontalAlignment.LEFT)

        column_main_info = Column(items=[card_title], width=35)
        column_set_combination = ColumnSet([column_main_info])

        adaptive_card_with_data = AdaptiveCard(body=[column_set_combination])
        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": adaptive_card_with_data.to_dict()
        }

        return attachment
