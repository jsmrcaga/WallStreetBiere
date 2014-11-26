#!/bin/python
# -*- coding:utf-8 -*-

import configparser
import datetime
import os
import payutcli
import pprint
import sqlite3
import time

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(ROOT_DIR, 'template')))

class WallStreet:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read([
            os.path.join(ROOT_DIR, 'defaults.ini'),
            os.path.join(ROOT_DIR, 'local_settings.ini'),
        ])
        self.client = payutcli.Client(**dict(self.config.items('client')))
        self.auth()
        self.backup = self.get_products()

    def auth(self):
        self.client.call("ADMINRIGHT", "loginApp", key=self.config.get("rights", "key"))
        self.client.call("POSS3", "loginBadge", badge_id=self.config.get("rights", "badge_id"), pin=self.config.get("rights", "pin"))

    def get_products(self):
        products = self.client.call("GESARTICLE", "getProducts", fun_id=2)
        beers = []
        for product in products:
            if product['alcool'] and product['active']:
                beers.append(product)
        return beers

    def get_stats(self, obj_id):
        today = datetime.date.today()
        today = "%d-%d-%d" % (today.year, today.month, today.day - 1)
        stats = self.client.call("STATS", "getNbSell", fun_id=2, obj_id=obj_id, start=today, tick=60*3)
        return stats

    def init_cycle(self):
        self.beers = self.get_products()
        self.sold_by_beer = []
        self.coef_by_beer = []
        self.total_beer = 0
        self.sold_last_period = []
        self.coef_last_period = []
        self.total_last_period = 0
        for i in range(len(self.backup)):
            self.sold_by_beer.append(0)
            self.coef_by_beer.append(0)
            self.sold_last_period.append(0)
            self.coef_last_period.append(0)

    def render_template(self):
        template = env.get_template('index.html')
        with open(os.path.join('www', 'index.html'), 'w') as index:
            index.write(template.render())

    def restore_backup(self):
        for beer in self.backup:
            self.client.call("GESARTICLE", "setProducts", fun_id=2,
                             obj_id=beer['id'],
                             name=beer['name'],
                             parent=beer['category_id'],
                             prix=beer['price'],
                             stock=beer['stock'],
                             alcool=beer['alcool'],
                             image=beer['image'],
                             tva=beer['tva'],
                             cotisant=beer['cotisant'],
                             active=beer['active'],
                             return_of=beer['return_of'])


    def run(self):
        self.init_cycle()
        while True:
            time.sleep(60*3)
            self.synthetize_stats()
            self.set_prices()
            self.render_template()
            hour = datetime.datetime.now().hour
            minutes = datetime.datetime.now().minute
            if hour >=21 and minutes >= 30:
                    self.restore_backup()

    def set_prices(self):
        # setProduct($obj_id = null, $name, $parent, $prix, $stock, $alcool, $image, $fun_id, $tva=0.00, $cotisant=1, $active=1, $return_of=NULL, $meta="[]")
        for indice, beer in enumerate(self.beers):
            old_price = int(beer['price'])
            beer['old_price'] = old_price
            new_price = (old_price * self.coef_last_period[indice]
                         + old_price * self.coef_by_beer[indice]) / 2
            beer['price'] = str(new_price)
            self.client.call("GESARTICLE", "setProducts", fun_id=2,
                             obj_id=beer['id'],
                             name=beer['name'],
                             parent=beer['category_id'],
                             prix=beer['price'],
                             stock=beer['stock'],
                             alcool=beer['alcool'],
                             image=beer['image'],
                             tva=beer['tva'],
                             cotisant=beer['cotisant'],
                             active=beer['active'],
                             return_of=beer['return_of'])

    def synthetize_stats(self):
        # get slices of the sells by time
        for indice, beer in enumerate(self.beers):
            pprint.pprint("test")
            # get the number of sells for each product
            stats = self.get_stats(beer['id'])
            last_period = stats.pop()
            # sum the number of beers sold for each beer
            for tick in stats:
                self.sold_by_beer[indice] += int(tick[0])
            # get the number of beers sold on last period, for each beer
            self.sold_last_period[indice] = int(last_period[0])
        # get totals from the 2 periods
        self.total_beer = sum(self.sold_by_beer)
        self.total_last_period = sum(self.sold_last_period)
        # compute coeficients
        for indice, beer in enumerate(self.beers):
            self.coef_by_beer[indice] = (self.sold_by_beer[indice]
                                         - self.total_beer) / total
            self.coef_last_period[indice] = (self.sold_last_period[indice]
                                             - self.total_last_period) / total


if __name__ == '__main__':
    w = WallStreet()
    w.run()
    # for beer in w.backup:
    #     pprint.pprint(w.get_stats(beer))
    # pprint.pprint(w.get_products())
