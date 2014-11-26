#!/bin/python
# -*- coding:utf-8 -*-

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

    def restore_backup(self, beers=None):
        """save all beers after modifying it"""
        beers = (beers if beers else self.beers)
        for beer in beers:
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
                         image=(product['image'] if product['image'] != None else "None"),
                         tva=product['tva'],
                         cotisant=product['cotisant'],
                         active=product['active'],
                         return_of=product['return_of'],
                         meta=product['meta'])

    def set_meta(self, id, key, value):
        """save in the meta of the product with id the key-value pair,
        or update it if it already exists"""
        product  = self.get_product(id)
        product['meta'] = json.dumps({key: value})
        self.save_product(product)


if __name__ == "__main__":
    import IPython
    b = ProductManager()
    IPython.embed()
