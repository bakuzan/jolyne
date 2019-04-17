from datetime import datetime, timedelta
import praw
import time
import os
import sys
import re
import logging
import login
import config as cfg

logging.basicConfig(filename='logfile.log', level=logging.INFO)

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def log_info(inp):
    logging.info(inp.encode('utf-8'))


def format_timestamp(inp):
    return inp.strftime("%Y-%m-%d %H:%M:%S")


def read_text_file(file_name):
    file_location = os.path.join(__location__, file_name)
    with open(file_location, "r") as f:
        data = f.read()
        data = data.split("\n")
        data = list(filter(None, data))
    logging.info("Read file %s" % (file_location))
    return data


def update_replied_to(posts_replied_to):
    file_location = os.path.join(__location__, "posts_replied_to.txt")
    with open(file_location, "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")


def get_replied_to():
    file_location = os.path.join(__location__, "posts_replied_to.txt")
    if not os.path.isfile(file_location):
        posts_replied_to = []

    # If we have run the code before, load the list of posts we have replied to
    else:
        posts_replied_to = read_text_file("posts_replied_to.txt")

    return posts_replied_to


def extract_search_terms(watched_terms, comment):
    comment_text = comment.body.lower()
    matches = [s for s in watched_terms if s in comment_text]
    return matches


def run_bot(reddit, created_since, options):
    posts_replied_to = get_replied_to()
    watched_terms = read_text_file("terms.txt")
    comments = reddit.subreddit(options["subreddits"]).comments(
        limit=int(options["comment_limit"]))

    for idx, comment in enumerate(comments):
        comment_created_at = datetime.utcfromtimestamp(comment.created_utc)

        if idx == 0:
            created_utc = comment_created_at

        if comment_created_at < created_since:
            continue

        logging.info("Comment: %s, by %s @ %s" %
                     (comment.id, comment.author, format_timestamp(comment_created_at)))

        # If we haven't replied to this post before
        if comment.id not in posts_replied_to:
            terms = extract_search_terms(watched_terms, comment)
            if len(terms) > 0:
                logging.info(
                    "Bot found terms @ https://www.reddit.com%s" % comment.permalink)
                log_info("Comment body: %s" % (comment.body))
                logging.info("Terms found: %s " % (terms))

                # Store the current id into our list
                posts_replied_to.append(comment.id)

    update_replied_to(posts_replied_to)
    return created_utc


if __name__ == "__main__":
    while True:
        try:
            c = cfg.load_config()
            opts = c.options
            reddit = login.login(c.reddit)
            # Start searching in last x hours
            created_utc = datetime.utcnow(
            ) - timedelta(hours=int(opts["search_start_hours_ago"]))

            while True:
                logging.info("Running bot, Fetching comments since %s" %
                             format_timestamp(created_utc))
                created_utc = run_bot(reddit, created_utc, opts)
                time.sleep(10)

        except praw.exceptions.APIException as e:
            logging.warn(e)
            logging.warn("Rate limit exceeded. Sleeping for 1 minute.")
            time.sleep(60)
        except KeyboardInterrupt:
            logging.info("Exiting...")
            sys.exit()
        except Exception as e:
            logging.exception(e)
            logging.error(str(e.__class__.__name__) + ": Sleeping for 15s")
            time.sleep(15)
