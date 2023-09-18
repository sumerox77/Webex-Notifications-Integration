from typing import Any


class RequestParser:
    def __init__(self):
        ...

    @staticmethod
    def parse_pr(payload: dict) -> dict[str, Any]:
        """This is the method dedicated to parse the 'pull request' payload from GitHub."""
        github_action = payload["action"]
        github_pull_request = payload["pull_request"]
        github_pull_request_id = github_pull_request["id"]
        html_url = github_pull_request["html_url"]
        title = github_pull_request["title"]
        project_name = github_pull_request["head"]["repo"]["name"]
        return {"title": title, "action": github_action, "link": html_url, "project_name": project_name,
                "pull_request_id": github_pull_request_id}

    @staticmethod
    def parse_pr_review(payload: dict) -> dict[str, Any]:
        """This is the method dedicated to parse the 'pull request review' payload from GitHub."""
        github_review = payload["review"]
        github_review_state = github_review["state"]
        github_action = payload["action"]
        github_pull_request = payload["pull_request"]
        github_pull_request_id = github_pull_request["id"]
        github_pull_request_link = github_pull_request["html_url"]
        html_url = github_pull_request["html_url"]
        title = github_pull_request["title"]
        project_name = github_pull_request["head"]["repo"]["name"]
        user = github_review["user"]
        reviewed_by = user["login"]
        reviewed_by_url = user["html_url"]
        review_requested_by = github_pull_request["user"]["login"]
        review_requested_by_link = github_pull_request["user"]["html_url"]
        return {"title": title, "action": github_action, "link": html_url, "project_name": project_name,
                "pull_request_id": github_pull_request_id, "state": github_review_state, "reviewed_by": reviewed_by,
                "reviewed_by_url": reviewed_by_url, "github_pr_link": github_pull_request_link,
                "review_requested_by": review_requested_by, "review_requested_by_link": review_requested_by_link
                }

    @staticmethod
    def parse_circle_ci(payload: dict) -> dict:
        """This is the method dedicated to parse the payload from CircleCI."""
        workflow = payload["workflow"]
        workflow_status = workflow["status"]
        workflow_url = workflow["url"]
        url = payload["pipeline"]["vcs"]["origin_repository_url"]
        commit = payload["pipeline"]["vcs"]["commit"]
        subject = commit["subject"]
        email_to_notify = commit["author"]["email"]
        branch_name = payload["pipeline"]["vcs"]["branch"]
        project_name = payload["project"]["name"]

        return {"subject_key": subject, "workflow_status_key": workflow_status, "github_url_key": url,
                "to_user_email": email_to_notify, "workflow_url_ci": workflow_url, "github_branch_name": branch_name,
                "project_name": project_name}

    @staticmethod
    def parse_issue(payload: dict):
        """This is the method dedicated to parse the 'issue' payload from GitHub"""
        issue = payload["issue"]
        issue_html_url = issue["html_url"]
        issue_user = issue["user"]
        issue_user_login = issue_user["login"]
        labels = issue["labels"]

        result = []
        for label in labels:
            result.append(label["name"])

        issue_labels = ", ".join(result)
        issue_title = issue["title"]

        return {"title": issue_title, "reporter": issue_user_login, "labels": issue_labels, "link_to": issue_html_url}
