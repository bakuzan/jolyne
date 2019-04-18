from datetime import datetime, timedelta
from logging import info
import psycopg2
import os


def earliest_run(opts):
    hours_ago = int(opts["search_start_hours_ago"])
    return datetime.utcnow() - timedelta(hours=hours_ago)


class JolyneDb:
    def __init__(self, db_opts, opts):
        self.__db_opts = db_opts
        self.__opts = opts
        self.__conn = None
        self.__cur = None
        self.connect()

    def connect(self):
        db = self.__db_opts
        self.__conn = psycopg2.connect(db['url'])
        self.__cur = self.__conn.cursor()
        info("Db connected")

    def disconnect(self):
        self.__conn.close()
        self.__conn.close()
        info("Db disconnected")

    def get_previous_runtime(self):
        self.__cur.execute("SELECT created_utc from comment_time")
        created_utc = self.__cur.fetchall()

        if (len(created_utc) > 0):
            created_utc = datetime(created_utc[0][0])
        else:
            created_utc = earliest_run(self.__opts)

        return created_utc

    def update_previous_runtime(self, ts):
        self.__cur.execute("UPDATE comment_time SET created_utc = '%s'" % (ts))
        self.__cur.execute("SELECT created_utc from comment_time")
        self.__conn.commit()

    def get_replied_to(self, last_runtime):
        ts = earliest_run(self.__opts)
        self.__cur.execute(
            "SELECT comment_id from replied_to where found_at > '%s'" % (ts))
        posts_replied_to = self.__cur.fetchall()
        return [s for (s,) in posts_replied_to]

    def update_replied_to(self, posts_replied_to):
        if len(posts_replied_to) > 0:
            args_str = ','.join(self.__cur.mogrify(
                "(%s, %s)", x).decode('utf-8') for x in posts_replied_to)
            query = "INSERT INTO replied_to (comment_id, found_at) VALUES " + \
                args_str
            print('query', query)
            self.__cur.execute(query)
            self.__conn.commit()

    def get_terms(self):
        self.__cur.execute("SELECT term from terms")
        terms = self.__cur.fetchall()
        return [s for (s,) in terms]
