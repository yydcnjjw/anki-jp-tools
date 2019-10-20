import atexit
import json
import os
from pathlib import Path

__APP_DIR = Path.home().joinpath('.my-tool')
if not os.path.exists(__APP_DIR):
    os.makedirs(__APP_DIR)

__CONF_FILE = __APP_DIR.joinpath('conf.json')
if not os.path.exists(__CONF_FILE):
    os.mknod(__CONF_FILE)
try:
    with open(__CONF_FILE, 'r') as fp:
        __conf = json.load(fp)
except Exception as e:
    print(e)
    __conf = {}


def get_conf(key):
    return __conf.get(key)


def put_conf(key, value):
    __conf[key] = value


def __save_conf():
    with open(__CONF_FILE, 'w') as fp:
        json.dump(__conf, fp)


atexit.register(__save_conf)
