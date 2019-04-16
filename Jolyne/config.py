from os import path
import configparser


class Config:
    def __init__(self):
        self.reddit = None


def load_config():
    config = Config()
    data = read_config_file()

    if "reddit" in data:
        d = data["reddit"]
        config.reddit = d

    return config


def read_config_file():
    conf = configparser.ConfigParser()
    file_path = get_config_ini_path()
    success = conf.read(file_path)

    if len(success) == 0:
        print("Failed to load config")
        return None

    return conf


def get_config_ini_path():
    base_path = path.dirname(__file__)
    return path.abspath(path.join(base_path, "..", "config.ini"))
