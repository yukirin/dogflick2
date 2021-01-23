#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import json
from urllib.parse import urlencode
from tornado.httpclient import AsyncHTTPClient


class Flickr:
    def __init__(self, api_key):
        self.api_key = api_key

    def parse(self, res):
        photos = json.loads(res.body.decode('utf-8'))
        stat = True if photos['stat'] == 'ok' else False
        photo_stat = True if photos['photos']['photo'] else False
        return stat and photo_stat, photos

    def fetch(self, page, timeout=20.0):
        return AsyncHTTPClient().fetch(
            "https://api.flickr.com/services/rest/?" + urlencode(self.build_query(page)),
            request_timeout=timeout
        )

    def build_query(self, page):
        return {
            'method': 'flickr.photos.search',
            'api_key': self.api_key,
            'tag_mode': 'AND',
            'text': 'dog cute',
            'license': '1,2,3,4,5,6',
            'sort': 'relevance',
            'extras': 'url_n,owner_name,url_l',
            'per_page': '20',
            'format': 'json',
            'nojsoncallback': '1',
            'page': page
        }


class FlickrCache:
    def __init__(self, db):
        self.db = db

    def hit(self, page):
        return self.db.dogflick.find_one({'page': page})

    def save(self, doc):
        doc['page'] = doc['photos']['page']
        doc['createdAt'] = datetime.utcnow()  # set ttl
        return self.db.dogflick.update(
            {'page': doc['page']}, {'$setOnInsert': doc}, upsert=True)
