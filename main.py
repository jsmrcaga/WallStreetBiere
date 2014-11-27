#!/bin/python
# -*- coding:utf-8 -*-

import configparser
import datetime
import os
import payutcli
import pprint
import productManager
import time

from codecs import open
from jinja2 import Environment, FileSystemLoader

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(ROOT_DIR, 'template')))

def FormatDecimal(value):
        return "{0:0.2f}".format(float(value))

env.filters.update({'FormatDecimal': FormatDecimal})

class WallStreet:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read([
            os.path.join(ROOT_DIR, 'defaults.ini'),
            os.path.join(ROOT_DIR, 'local_settings.ini'),
        ])
        self.client = payutcli.Client(**dict(self.config.items('client')))
        self.auth()
        self.pm = productManager.ProductManager(self.client)
        self.backup = self.pm.get_products()

    def auth(self):
        self.client.call("ADMINRIGHT", "loginApp", key=self.config.get("rights", "key"))
        self.client.call("POSS3", "loginBadge", badge_id=self.config.get("rights", "badge_id"), pin=self.config.get("rights", "pin"))

    def get_stats(self, obj_id):
        today = datetime.date.today()
        today = "%d-%d-%d" % (today.year, today.month, today.day - 1)
        stats = self.client.call("STATS", "getNbSell", fun_id=2, obj_id=obj_id, start=today, tick=3*60)
        return stats

    def init_cycle(self):
        self.sold_by_beer = []
        self.coef_by_beer = []
        self.total_beer = 0.
        self.sold_last_period = []
        self.coef_last_period = []
        self.total_last_period = 0.
        self.lost_money = 0.
        for i in range(len(self.backup)):
            self.sold_by_beer.append(0)
            self.coef_by_beer.append(0)
            self.sold_last_period.append(0)
            self.coef_last_period.append(0)

    def init_data(self):
        self.beers = self.pm.get_products()
        for beer in self.beers:
            print beer['name']
            self.pm.set_meta(beer['id'], 'total_sold', 0)
            self.pm.set_meta(beer['id'], 'sold_last_period', 0)
            self.pm.set_meta(beer['id'], 'initial_price', beer['price'])
            self.pm.set_meta(beer['id'], 'money_made', 0)
            self.pm.set_meta(beer['id'], 'date_last_period', time.time())
            #self.pm.set_meta(beer['id'], 'price_last_period', 0)

    def render_template(self):
        for i in self.beers:
            i['price'] = float(i['price']) / 100.
            i['old_price'] = float(i['old_price']) / 100.
        template = env.get_template('index.html')
        with open(os.path.join('www', 'index.html'), 'w', encoding='utf-8') as index:
            index.write(template.render(beers=self.beers))

    def run(self):
        self.init_data()
        while True:
            self.init_cycle()
            self.beers = self.pm.get_products()
            time.sleep(60*3)
            self.synthetize_stats()
            self.set_prices()
            self.render_template()
            hour = datetime.datetime.now().hour
            minutes = datetime.datetime.now().minute
            if hour >=21 and minutes >= 35:
                    self.pm.restore_backup(self.backup)

    def set_prices(self):
        # setProduct($obj_id = null, $name, $parent, $prix, $stock, $alcool, $image, $fun_id, $tva=0.00, $cotisant=1, $active=1, $return_of=NULL, $meta="[]")
        for indice, beer in enumerate(self.beers):
            old_price = beer['old_price']
            new_price = (old_price * self.coef_last_period[indice]
                         + old_price * self.coef_by_beer[indice]) / 2
            beer['price'] = str(new_price)
            if beer['price'] <= 0:
                beer['price'] = beer['meta']['initial_price']
            self.pm.save_product(beer)

    def sum_sold_by_tick(self, the_list):
        total = 0
        if len(the_list) == 0:
            return 0
        for i in the_list:
            total += int(i[0])
        return total

    def synthetize_stats(self):
        # get slices of the sells by time
        for indice, beer in enumerate(self.beers):
            print beer['name']
            # get number of beers sold on last period
            try:
                last_date = float(beer['meta']['date_last_period'])
            except:
                pass
            tick = time.time() - last_date
            stats = self.get_stats(beer['id'])
            try:
                nb_sold_last_period = int(stats.pop()[0])
            except IndexError:
                nb_sold_last_period = 0

            # save important variables
            beer['last_period'] = last_date
            beer['sold_last_period'] = nb_sold_last_period
            beer['old_price'] = int(beer['price'])
            beer['total_sold'] = self.sum_sold_by_tick(stats)
            beer['money_made'] = int(beer['meta']['money_made']) + nb_sold_last_period * beer['old_price']
            beer['standard_money'] = beer['total_sold'] * int(beer['meta']['initial_price'])

            # synthetize stats
            self.sold_by_beer[indice] = beer['total_sold']
            self.sold_last_period[indice] = nb_sold_last_period
            self.total_beer += beer['total_sold']
            self.total_last_period += nb_sold_last_period

        # compute general stats
        self.total_beer = sum(self.sold_by_beer)
        self.total_last_period = sum(self.sold_last_period)

        # compute coefficients. Average of what we should have sold
        self.total_beer /= len(self.beers) * 1.
        self.total_last_period /= len(self.beers) * 1.
        for indice, beer in enumerate(self.beers):
            self.coef_by_beer[indice] = 1. - (self.total_beer
                                         - self.sold_by_beer[indice]) / self.total_beer
            self.coef_last_period[indice] = 1. - (self.total_last_period
                                             - self.sold_last_period[indice]) / self.total_beer


if __name__ == '__main__':
    import IPython
    w = WallStreet()
    w.beers = w.pm.get_products()
    #w.init_data()
    w.init_cycle()
    w.synthetize_stats()
    IPython.embed()
    # w.run()
    # for beer in w.backup:
    #     pprint.pprint(w.get_stats(beer))
    # pprint.pprint(w.get_products())
