import os
import sys
import logging

if "IS_HEROKU" in os.environ:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
else:
    logging.basicConfig(filename='logfile.log', level=logging.INFO)


logger = logging.getLogger(name="app")


def log_info(inp):
    logger.info(inp.encode('utf-8'))
