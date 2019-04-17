from datetime import datetime, timedelta
from logging import info
import psycopg2
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class JolyneDb:
    def __init__(self, opts):
        self.__opts = opts
        self.__conn = None
        self.__cur = None
        self.connect()

    def connect(self):
        db = self.__opts
        self.__conn = psycopg2.connect(
            user=db["user"], password=db["password"],
            dbname=db["name"], port=db["port"])
        self.__cur = self.__conn.cursor()
        info("Db connected")

    def disconnect(self):
        self.__conn.close()
        self.__conn.close()
        info("Db disconnected")

    def get_previous_runtime(self, opts):
        self.__cur.execute("SELECT created_utc from comment_time")
        created_utc = self.__cur.fetchall()

        if (len(created_utc) > 0):
            created_utc = datetime(created_utc[0][0])
        else:
            created_utc = datetime.utcnow(
            ) - timedelta(hours=int(opts["search_start_hours_ago"]))

        return created_utc

    def update_previous_runtime(self, ts):
        self.__cur.execute("UPDATE comment_time SET created_utc = '%s'" % (ts))
        self.__cur.execute("SELECT created_utc from comment_time")
        self.__conn.commit()

    def get_replied_to(self):
        file_location = os.path.join(__location__, "posts_replied_to.txt")
        if not os.path.isfile(file_location):
            posts_replied_to = []

        # If we have run the code before, load the list of posts we have replied to
        else:
            posts_replied_to = self.__read_text_file("posts_replied_to.txt")

        return posts_replied_to

    def update_replied_to(self, posts_replied_to):
        file_location = os.path.join(__location__, "posts_replied_to.txt")
        with open(file_location, "w") as f:
            for post_id in posts_replied_to:
                f.write(post_id + "\n")

    def get_terms(self):
        return self.__read_text_file("terms.txt")

    def __read_text_file(self, file_name):
        file_location = os.path.join(__location__, file_name)
        with open(file_location, "r") as f:
            data = f.read()
            data = data.split("\n")
            data = list(filter(None, data))
        info("Read file %s" % (file_location))
        return data
