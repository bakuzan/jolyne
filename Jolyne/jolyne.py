from datetime import datetime, timedelta
import praw
import time
import os
import sys
import re
from logger import logger, log_info
import login
import config as cfg
from db import JolyneDb


def format_timestamp(inp):
    return inp.strftime("%Y-%m-%d %H:%M:%S")


def extract_search_terms(watched_terms, comment):
    comment_text = comment.body.lower()
    matches = [s for s in watched_terms if s in comment_text]
    return matches


def run_bot(reddit, created_since, db, options):
    new_posts_replied_to = []
    posts_replied_to = db.get_replied_to(created_since)
    watched_terms = db.get_terms()

    comments = reddit.subreddit(options["subreddits"]).comments(
        limit=int(options["comment_limit"]))

    for idx, comment in enumerate(comments):
        comment_created_at = datetime.utcfromtimestamp(comment.created_utc)

        if idx == 0:
            created_utc = comment_created_at

        if comment_created_at < created_since:
            continue

        logger.info("Comment: %s, by %s @ %s" %
                    (comment.id, comment.author, format_timestamp(comment_created_at)))

        # If we haven't replied to this post before
        if comment.id not in posts_replied_to:
            terms = extract_search_terms(watched_terms, comment)
            if len(terms) > 0:
                logger.info(
                    "Bot found terms @ https://www.reddit.com%s" % comment.permalink)
                log_info("Comment body: %s" % (comment.body))
                logger.info("Terms found: %s " % (terms))

                # Store the current id into our list
                new_posts_replied_to.append(
                    (comment.id, format_timestamp(comment_created_at)))

    db.update_previous_runtime(created_utc)
    db.update_replied_to(new_posts_replied_to)
    return created_utc


if __name__ == "__main__":
    while True:
        try:
            c = cfg.load_config()
            opts = c.options

            # Login to reddit
            reddit = login.login(c.reddit)

            # Get Db
            db = JolyneDb(c.db, opts)
            created_utc = db.get_previous_runtime()

            while True:
                logger.info("Running bot, Fetching comments since %s" %
                            format_timestamp(created_utc))
                created_utc = run_bot(reddit, created_utc, db, opts)
                time.sleep(10)

        except praw.exceptions.APIException as e:
            logger.warn(e)
            logger.warn("Rate limit exceeded. Sleeping for 1 minute.")
            time.sleep(60)
        except KeyboardInterrupt:
            db.disconnect()
            logger.info("Exiting...")
            sys.exit()
        except Exception as e:
            logger.exception(e)
            logger.error(str(e.__class__.__name__) + ": Sleeping for 15s")
            time.sleep(15)
