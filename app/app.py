from flask import Flask, request
from application.utils.request_parser import RequestParser
from application.facade.NotificationsFacade import NotificationsFacade
import logging

# ALLOWED PULL REQUEST ACTIONS
PULL_REQUEST_ALLOWED_ACTIONS = ["ready_for_review", "opened", "reopened"]
ISSUES_ALLOWED_ACTIONS = ["opened"]

# RESPONSES
NO_CONTENT = "Everything is Ok!", 204
ERROR_RESPONSE = "Error has occurred while processing the request.", 406
PING_RESPONSE = "Ping successful.", 200

# PATHS
GITHUB_PULL_REQUEST_PATH = "/pull-request-notifier"
GITHUB_PULL_REQUEST_REVIEWS_PATH = "/pull-request-review-notifier"

GITHUB_ISSUES_PATH = "/issue-notifier"

CIRCLE_CI_PATH = "/circle-ci-workflow-notifier"
TEST_PATH = "/test"

GITHUB_MAPPING_USERNAME = "/username_mapping"

# ALLOWED METHODS
ALLOWED_METHODS_POST = ['POST']

app = Flask(__name__)

notificationFacade = NotificationsFacade()
payload_parser = RequestParser()

SPACE_ID = "<>"


@app.route(TEST_PATH, methods=ALLOWED_METHODS_POST)
def webhook():
    request_log(TEST_PATH)

    message = ""
    for key, value in request.json.items():
        message += f"{key}, {value}\n"
    print(message)
    return 200


@app.route(GITHUB_ISSUES_PATH, methods=ALLOWED_METHODS_POST)
def github_issue_listener():
    request_log(GITHUB_ISSUES_PATH)

    parsed_payload = payload_parser.parse_issue(request.json)

    if ping_self(payload=request):
        return PING_RESPONSE
    # TODO: Before final update, turn on check for only opened issues.
    # if parsed_payload["action"] not in ISSUES_ALLOWED_ACTIONS:
    #     return ERROR_RESPONSE

    notificationFacade.github_issue_handler(payload=parsed_payload, space_id=SPACE_ID)
    return NO_CONTENT


@app.route(GITHUB_PULL_REQUEST_PATH, methods=ALLOWED_METHODS_POST)
def github_pull_request_listener():
    request_log(GITHUB_PULL_REQUEST_PATH)
    if ping_self(payload=request):
        return PING_RESPONSE

    parsed_payload = payload_parser.parse_pr(request.json)

    if parsed_payload["action"] not in PULL_REQUEST_ALLOWED_ACTIONS:
        return ERROR_RESPONSE

    notificationFacade.github_pull_request_handler(payload=parsed_payload, space_id=SPACE_ID)
    return NO_CONTENT


@app.route(GITHUB_PULL_REQUEST_REVIEWS_PATH, methods=ALLOWED_METHODS_POST)
def github_pull_request_review_listener():
    request_log(GITHUB_PULL_REQUEST_REVIEWS_PATH)

    parsed_payload = payload_parser.parse_pr_review(request.json)
    pull_request_state = parsed_payload["state"]
    notificationFacade.github_pull_request_review_handler(payload=parsed_payload, space_id=SPACE_ID,
                                                          state=pull_request_state)
    return NO_CONTENT


@app.route(CIRCLE_CI_PATH, methods=ALLOWED_METHODS_POST)
def circle_ci_request_listener():
    logging.info(f"Incoming POST request to: {CIRCLE_CI_PATH}")

    parsed_payload = payload_parser.parse_circle_ci(request.json)

    notificationFacade.circle_ci_handler(parsed_payload)
    return NO_CONTENT


@app.route(GITHUB_MAPPING_USERNAME, methods=ALLOWED_METHODS_POST)
def add_github_username_mapping():
    logging.info(f"Incoming POST request to: {GITHUB_MAPPING_USERNAME}")
    logging.info(f"EMAIL: {request.json['github_username']} USERNAME: {request.json['cisco_email']}")
    return notificationFacade.add_email_mapping_to_github_username(github_username=request.json['github_username'],
                                                                   cisco_email=request.json['cisco_email'])


@app.route(GITHUB_MAPPING_USERNAME, methods=['GET'])
def get_github_username():
    logging.info(f"Incoming GET request to: {GITHUB_MAPPING_USERNAME}")
    return notificationFacade.get_email_by_github_username(github_username=request.json['github_username'])


def ping_self(payload):
    return "zen" in dict(payload.json)


def request_log(path):
    logging.info(f"Incoming POST request to: {path}")


if __name__ == "__main__":
    app.run()
