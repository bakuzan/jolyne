import praw
import time
import os
import re
import logging
import login
import config as cfg

logging.basicConfig(filename='logfile.log', level=logging.INFO)


def get_watched_terms():
    with open("watched_terms.txt", "r") as f:
        watched_terms = f.read()
        watched_terms = watched_terms.split("\n")
        watched_terms = list(filter(None, watched_terms))
    logging.info("Current watched terms loaded: ", watched_terms)
    return watched_terms


def update_replied_to(posts_replied_to):
    # Write our updated list back to the file
    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")


def get_replied_to():
    # Have we run this code before? If not, create an empty list
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []

    # If we have run the code before, load the list of posts we have replied to
    else:
        # Read the file into a list and remove any empty values
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    return posts_replied_to


def extract_search_terms(watched_terms, comment):
    comment_text = comment.body.lower()
    matches = [term for term in comment_text for term in watched_terms]
    return matches


def run_bot(reddit, options):
    posts_replied_to = get_replied_to()
    watched_terms = get_watched_terms()
    subreddits = reddit.subreddit(options["subreddits"])

    for submission in subreddits.hot(limit=10):
        logging.info("Submission > ", submission.title,
                     submission.num_comments)

        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            # If we haven't replied to this post before
            if comment.id not in posts_replied_to:
                terms = extract_search_terms(watched_terms, comment)
                if len(terms) > 0:
                    # Reply to the post
                    # submission.reply("BOT SHOUTING TEST MESSAGE USING PYTHON")
                    logging.info("Bot found terms in submission: %s, comment: %s " % (
                        submission.title, comment.id))
                    logging.info("Body: %s " % comment.body)
                    logging.info("Terms: %s " % terms)

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
            sys.exit()
        except Exception as e:
            logging.exception(e)
            logging.error(str(e.__class__.__name__) + ": Sleeping for 15s")
            time.sleep(15)
