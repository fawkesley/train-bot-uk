import json
import logging
import os
import traceback

from pprint import pformat

import requests

from .config import REPORT_ERRORS_TO_GITHUB

LOG = logging.getLogger(__name__)

URL = 'https://api.github.com/repos/paulfurley/train-bot-uk/issues'

__all__ = ['create_github_issue']


def create_github_issue(inbound_message):
    if not REPORT_ERRORS_TO_GITHUB:
        return '<no url available>'

    token = get_token()

    json = make_json(inbound_message)

    return call_api_make_issue(token, json)


def get_token():
    return os.environ['GITHUB_TOKEN']


def call_api_make_issue(token, json):
    headers = {
        'User-Agent': 'paulfurley',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(token),
    }

    response = requests.post(URL, headers=headers, data=json)

    try:
        response.raise_for_status()
    except:
        LOG.error(response.content)
        raise

    if response.status_code == 201:
        return convert_api_issue_url_to_www(response.headers['location'])


def make_json(inbound_message):
    body = (
        "Full message:\n"
        "```\n"
        "{message}\n"
        "```\n"
        "The error was:\n"
        "```\n"
        "{error}"
        "```\n").format(message=pformat(inbound_message),
                        error=traceback.format_exc())

    return json.dumps({
        "title": "Error processing: `{}`".format(inbound_message.content),
        "body": body,
        "assignee": "paulfurley",
        "labels": ["auto-created"]
    })


def convert_api_issue_url_to_www(api_url):
    """
    Convert eg:
        `https://api.github.com/repos/paulfurley/train-bot-uk/issues/43`
    into
        `https://github.com/paulfurley/train-bot-uk/issues/43`
    """
    return api_url.replace('api.github.com/repos', 'github.com')
