#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao (askxuefeng@gmail.com)'

'''
Util app that contains useful functions such as proxy.
'''

from urllib2 import urlparse
from urllib2 import unwrap
from exweb import context

from google.appengine.api import memcache
from google.appengine.ext import db
import random

class GeneralCounterShardConfig(db.Model):
    '''
    Tracks the number of shards for each named counter.
    '''
    name = db.StringProperty(required=True)
    num_shards = db.IntegerProperty(required=True, default=10)

class GeneralCounterShard(db.Model):
    '''
    Shards for each named counter.
    '''
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(required=True, default=0)

def get_count(name):
    '''
    Retrieve the value for a given sharded counter.
    
    Args:
        name - The name of the counter
    '''
    total = memcache.get(name)
    if total is None:
        total = 0
        for counter in GeneralCounterShard.all().filter('name = ', name):
            total += counter.count
        memcache.add(name, str(total), 60)
    return total

def increment(name):
    """Increment the value for a given sharded counter.

    Parameters:
      name - The name of the counter
    """
    config = GeneralCounterShardConfig.get_or_insert(name, name=name)
    def txn():
        index = random.randint(0, config.num_shards - 1)
        shard_name = name + str(index)
        counter = GeneralCounterShard.get_by_key_name(shard_name)
        if counter is None:
            counter = GeneralCounterShard(key_name=shard_name, name=name)
        counter.count += 1
        counter.put()
    db.run_in_transaction(txn)
    memcache.incr(name)

def increase_shards(name, num):
    """Increase the number of shards for a given sharded counter.
    Will never decrease the number of shards.

    Parameters:
      name - The name of the counter
      num - How many shards to use

    """
    config = GeneralCounterShardConfig.get_or_insert(name, name=name)
    def txn():
        if config.num_shards < num:
            config.num_shards = num
            config.put()
    db.run_in_transaction(txn)

def make_proxy(url):
    '''
    Make a proxy url for given url. For example, a given url 'http://a.b.c/xyz.png' 
    will be proxied like 'http://your-app.appspot.com/util/proxy/http://a_b_c/xyz.png'.
    '''
    us = urlparse.urlparse(url)
    uus = (us[0], us[1].replace('.', '_'), us[2], us[3], us[4], us[5])
    return '/util/proxy/' + urlparse.urlunparse(uus)
