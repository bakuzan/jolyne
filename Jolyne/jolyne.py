import praw
import time
import os
import re
import logging
import login
import config as cfg

logging.basicConfig(filename='logfile.log', level=logging.INFO)

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


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


def run_bot(reddit, options):
    posts_replied_to = get_replied_to()
    watched_terms = read_text_file("terms.txt")
    subreddits = reddit.subreddit(options["subreddits"])

    for submission in subreddits.hot(limit=options["submission_limit"]):
        logging.info("Submission: %s with %s comments " % (submission.title,
                                                           submission.num_comments))

        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            # If we haven't replied to this post before
            if comment.id not in posts_replied_to:
                terms = extract_search_terms(watched_terms, comment)
                if len(terms) > 0:
                    logging.info("Bot found terms in submission: %s, comment: %s " % (
                        submission.title, comment.id))
                    logging.info("Body: %s " % (comment.body))
                    logging.info("Terms: %s " % (terms))

                    # Store the current id into our list
                    posts_replied_to.append(comment.id)

    update_replied_to(posts_replied_to)


if __name__ == "__main__":
    while True:
        try:
            c = cfg.load_config()
            reddit = login.login(c.reddit)

            while True:
                logging.info("Running bot, Fetching comments..")
                run_bot(reddit, c.options)
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
