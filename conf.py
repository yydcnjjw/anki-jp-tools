import atexit
import json
import os
from pathlib import Path

__APP_DIR = Path.home().joinpath('.my-tool')
if not os.path.exists(__APP_DIR):
    os.makedirs(__APP_DIR)

__CONF_FILE = __APP_DIR.joinpath('conf.json')


def get_conf(key):
    return __conf.get(key)


def put_conf(key, value):
    __conf[key] = value


def __save_conf():
    with open(__CONF_FILE, 'w') as fp:
        json.dump(__conf, fp)


try:
    if not os.path.exists(__CONF_FILE):
        __conf = {}
        __save_conf()
    else:
        with open(__CONF_FILE, 'r') as fp:
            __conf = json.load(fp)
except Exception as e:
    print(e)

atexit.register(__save_conf)
