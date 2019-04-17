from os import path, environ
import logging


class Config:
    def __init__(self):
        self.reddit = None
        self.options = None
        self.db = None


def load_config():
    config = Config()

    config.reddit = {
        client_id: environ.get('REDDIT_CLIENT_ID'),
        client_secret: environ.get('REDDIT_CLIENT_SECRET'),
        password: environ.get('REDDIT_PASSWORD'),
        username: environ.get('REDDIT_USERNAME'),
        user_agent: environ.get('REDDIT_USER_AGENT')
    }

    config.options = {
        subreddits: environ.get('OPT_SUBREDDITS'),
        comment_limit: environ.get('OPT_COMMENT_LIMIT'),
        search_start_hours_ago: environ.get('OPT_SEARCH_START_HOURS_AGO')
    }

    config.db = {
        user: environ.get('DB_USER'),
        password: environ.get('DB_PASSWORD'),
        port: environ.get('DB_PORT'),
        name: environ.get('DB_NAME')
    }

    return config
