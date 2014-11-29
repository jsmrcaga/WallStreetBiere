#!/bin/python
# -*- coding:utf-8 -*-

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
