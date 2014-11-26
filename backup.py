#!/bin/python
# -*- coding:utf-8 -*-

import configparser
import datetime
import json
import os
import payutcli
import pprint

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

class Backup:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read([
            os.path.join(ROOT_DIR, 'defaults.ini'),
            os.path.join(ROOT_DIR, 'local_settings.ini'),
        ])
        self.client = payutcli.Client(**dict(self.config.items('client')))
        self.auth()
        self.beers = self.get_products()

    def auth(self):
        """connect to payutc server"""
        self.client.call("ADMINRIGHT", "loginApp", key=self.config.get("rights", "key"))
        self.client.call("POSS3", "loginBadge", badge_id=self.config.get("rights", "badge_id"), pin=self.config.get("rights", "pin"))

    def get_products(self):
        """save in self.beers all the beers"""
        products = self.client.call("GESARTICLE", "getProducts", fun_id=2)
        beers = []
        for product in products:
            if product['alcool'] and product['active']:
                beers.append(product)
        return beers

    def get_product(self, id):
        """get data of one product from server"""
        product = self.client.call("GESARTICLE", "getProduct", obj_id=id, fun_id=2)
        try:
            return product['success']
        except:
            print("Impossible to retrieve this article")

    def restore_backup(self):
        """save all beers after modifying it"""
        for beer in self.beers():
            self.save_product(beer)

    def save_product(self, product):
        """save a product given in parameters"""
        self.client.call("GESARTICLE", "setProduct", fun_id=2,
                         obj_id=product['id'],
                         name=product['name'],
                         parent=product['categorie_id'],
                         prix=product['price'],
                         stock=product['stock'],
                         alcool=product['alcool'],
                         image=product['image'],
                         tva=product['tva'],
                         cotisant=product['cotisant'],
                         meta=product['meta'])

    def set_meta(self, id, key, value):
        """save in the meta of the product with id the key-value pair,
        or update it if it already exists"""
        product  = self.get_product(id)
        product['meta'] = json.dumps({key: value})
        self.save_product(product)


if __name__ == "__main__":
    import IPython
    b = Backup()
    IPython.embed()
