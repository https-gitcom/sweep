import asyncio
import datetime
import os
import time
from itertools import chain, islice

from github import Github
from github.Event import Event
from github.IssueEvent import IssueEvent
from github.Repository import Repository

from sweepai.api import handle_request
from sweepai.utils.event_logger import logger

DEBUG = os.environ.get("DEBUG", False)


def pascal_to_snake(name):
    return "".join(["_" + i.lower() if i.isupper() else i for i in name]).lstrip("_")


def get_event_type(event: Event | IssueEvent):
    if isinstance(event, IssueEvent):
        return "issues"
    else:
        return pascal_to_snake(event.type)[: -len("_event")]


def stream_events(repo: Repository, timeout: int = 2, offset: int = 2 * 60):
    processed_event_ids = set()
    current_time = time.time() - offset
    local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

    while True:
        events_iterator = chain(repo.get_events(), islice(repo.get_issues_events(), 60))
        for event in events_iterator:
            if event.id not in processed_event_ids:
                local_time = event.created_at.replace(
                    tzinfo=datetime.timezone.utc
                ).astimezone(local_tz)

                if local_time.timestamp() > current_time:
                    yield event
                else:
                    if DEBUG:
                        logger.debug(
                            f"Skipping event {event.id} because it is too old ({local_time})"
                        )
            if DEBUG:
                logger.debug(f"Skipping event {event.id} because it is already handled")
            processed_event_ids.add(event.id)
        time.sleep(timeout)


g = Github(os.environ["GITHUB_PAT"])
repo_name = os.environ["REPO"]
repo = g.get_repo(repo_name)
if DEBUG:
    logger.debug("Debug mode enabled")
print(f"Starting server, listening to events from {repo_name}...")
print(
    f"To create a PR, please create an issue at https://github.com/{repo_name}/issues with a title prefixed with 'Sweep:'"
)
for event in stream_events(repo):
    if isinstance(event, IssueEvent):
        payload = event.raw_data
        payload["action"] = payload["event"]
    else:
        payload = {**event.raw_data, **event.payload}
    payload["sender"] = payload.get("sender", payload["actor"])
    payload["sender"]["type"] = "User"
    payload["pusher"] = payload.get("pusher", payload["actor"])
    payload["pusher"]["name"] = payload["pusher"]["login"]
    payload["pusher"]["type"] = "User"
    payload["after"] = payload.get("after", payload.get("head"))
    payload["repository"] = repo.raw_data
    payload["installation"] = {"id": -1}
    logger.info(str(event) + " " + str(event.created_at))
    handle_request(payload, get_event_type(event))
