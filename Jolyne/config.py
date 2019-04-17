from os import path
import logging
import configparser


class Config:
    def __init__(self):
        self.reddit = None
        self.options = None
        self.db = None


def load_config():
    config = Config()
    data = read_config_file()

    if "reddit" in data:
        d = data["reddit"]
        config.reddit = d

    if "options" in data:
        d = data["options"]
        config.options = d

    if "db" in data:
        d = data["db"]
        config.db = d

    return config


def read_config_file():
    conf = configparser.ConfigParser()
    file_path = get_config_ini_path()
    success = conf.read(file_path)

    if len(success) == 0:
        logging.warn("Failed to load config from %s" % file_path)
        return None

    return conf


def get_config_ini_path():
    base_path = path.dirname(__file__)
    return path.abspath(path.join(base_path, "..", "config.ini"))
