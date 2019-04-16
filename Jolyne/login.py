import praw
import os


def login(config):
    print("Logging in..", config)
    r = None

    try:
        r = praw.Reddit(
            username=config["username"],
            password=config["password"],
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            user_agent=config["user_agent"])
        print("Logged in!")

    except:
        print("Failed to log in!")

    return r
