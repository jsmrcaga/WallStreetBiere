#!/bin/python
# -*- coding:utf-8 -*-

import configparser
import json
import os
import payutcli
import productManager

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

config = configparser.ConfigParser()
config.read([
    os.path.join(ROOT_DIR, 'defaults.ini'),
    os.path.join(ROOT_DIR, 'local_settings.ini'),
])

client = payutcli.Client(**dict(config.items('client')))
client.call("ADMINRIGHT", "loginApp", key=config.get("rights", "key"))
client.call("POSS3", "loginBadge", badge_id=config.get("rights", "badge_id"), pin=config.get("rights", "pin"))

data = json.loads(open('backup.txt', 'r').read())
pm = productManager.ProductManager(client)
pm.restore_backup(data)
