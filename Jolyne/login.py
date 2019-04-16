import praw
import os
import logging


def login(config):
    logging.info("Logging in..")
    r = None

    try:
        r = praw.Reddit(
            username=config["username"],
            password=config["password"],
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            user_agent=config["user_agent"])
        logging.info("Logged in successful")

    except Exception as e:
        logging.exception()
        logging.error("Failed to log in")

    return r
