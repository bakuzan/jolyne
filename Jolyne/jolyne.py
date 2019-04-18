from datetime import datetime, timedelta
import praw
import time
import os
import sys
import re
import schedule
from logger import logger, log_info
import login
import config as cfg
from db import JolyneDb


def format_timestamp(inp):
    return inp.strftime("%Y-%m-%d %H:%M:%S")


def check_mail(db):
    for mail in reddit.inbox.unread(limit=None):
        if mail.body[:len("!blacklist")] == "!blacklist" and isinstance(mail, praw.models.Message):
            authour = mail.author
            db.opted_out(authour)

            reply_message = "You have been successfully blacklisted, /u/%s." % authour
            mail.reply(reply_message)

            logger.info("Blacklisted user /u/%s at their request." % authour)
        mail.mark_read()


def extract_search_terms(watched_terms, comment):
    comment_text = comment.body.lower()
    matches = [s for s in watched_terms if s in comment_text]
    return matches


def run_bot(reddit, created_since, db, redcfg, optcfg):
    new_posts_replied_to = []
    posts_replied_to = db.get_replied_to(created_since)
    watched_terms = db.get_terms()
    blacklist = db.get_blacklist()

    comments = reddit.subreddit(optcfg["subreddits"]).comments(
        limit=int(optcfg["comment_limit"]))

    for idx, comment in enumerate(comments):
        comment_created_at = datetime.utcfromtimestamp(comment.created_utc)

        if idx == 0:
            created_utc = comment_created_at

        if comment_created_at < created_since:
            continue

        cmt_id = comment.id
        authour = comment.author

        logger.info("Comment: %s, by %s @ %s" %
                    (cmt_id, authour, format_timestamp(comment_created_at)))

        is_self = authour == redcfg['username']
        not_blacklisted = authour not in blacklist
        has_no_reply = cmt_id not in posts_replied_to

        if has_no_reply and not_blacklisted and not is_self:
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
    c = cfg.load_config()
    opts = c.options
    redd = c.reddit

    # Login to reddit
    reddit = login.login(redd)

    # Get Db
    db = JolyneDb(c.db, opts)
    created_utc = db.get_previous_runtime()

    schedule.every().minute.do(check_mail, db)

    while True:
        try:
            while True:
                schedule.run_pending()
                logger.info("Running bot, Fetching comments since %s" %
                            format_timestamp(created_utc))
                created_utc = run_bot(reddit, created_utc, db, redd, opts)
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
