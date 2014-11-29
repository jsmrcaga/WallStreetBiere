#!/bin/python
# -*- coding:utf-8 -*-

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
# any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import configparser
import datetime
import json
import os
import payutcli
import pprint

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

class ProductManager:
    def __init__(self, payutc_client):
        self.config = configparser.ConfigParser()
        self.config.read([
            os.path.join(ROOT_DIR, 'defaults.ini'),
            os.path.join(ROOT_DIR, 'local_settings.ini'),
        ])
        self.client = payutc_client
        self.beers = self.get_products()

    def get_meta(self, id, key):
        """return the value of the given key in the meta of a product"""
        product = self.get_product(id)
        value = product['meta']
        return value[key]

    def get_products(self):
        """save in self.beers all the beers"""
        products = self.client.call("GESARTICLE", "getProducts", fun_id=2)
        beers = []
        for product in products:
            if product['alcool'] and product['active'] and product['name'] != "Westmalle Triple":
                beers.append(product)
        return beers

    def get_product(self, id):
        """get data of one product from server"""
        product = self.client.call("GESARTICLE", "getProduct", obj_id=id, fun_id=2)
        try:
            return product['success']
        except:
            print("Impossible to retrieve this article")

    def restore_backup(self, beers=None):
        """save all beers after modifying it"""
        beers = (beers if beers else self.beers)
        for beer in beers:
            beer['price'] = beer['meta']['initial_price']
            self.save_product(beer)

    def save_product(self, product):
        """save a product given in parameters"""
        meta = product['meta']
        try:
            meta['total_sold'] = product['total_sold']
            meta['sold_last_period'] = product['sold_last_period']
            meta['money_made'] = product['money_made']
            meta['date_last_period'] = product['date_last_period']
            meta['price_last_period'] = product['old_price']
            product['meta'] = meta
            for key, value in product['meta']:
                product['meta']['key'] = str(value)
        except KeyError:
            pass
        try:
            self.client.call("GESARTICLE", "setProduct", fun_id=2,
                             obj_id=product['id'],
                             name=product['name'],
                             parent=product['categorie_id'],
                             prix=product['price'],
                             stock=product['stock'],
                             alcool=product['alcool'],
                             image=(product['image'] if product['image'] != None else "0"),
                             tva=product['tva'],
                             cotisant=product['cotisant'],
                             active=product['active'],
                             return_of=product['return_of'],
                             meta=json.dumps(meta))
        except:
            print "*** ALERT ALERT ALERT ***"
            import pdb;pdb.set_trace()

    def set_meta(self, id, key, value):
        """save in the meta of the product with id the key-value pair,
        or update it if it already exists"""
        product  = self.get_product(id)
        meta = product['meta']
        meta[key] = value
        product['meta'] = meta
        self.save_product(product)


if __name__ == "__main__":
    import IPython
    b = ProductManager()
    IPython.embed()
