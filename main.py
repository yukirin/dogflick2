#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pathlib

import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.httpclient import HTTPError
from motor import MotorClient
from tornado.options import parse_command_line

import flickr


class DogFlickApp(tornado.web.Application):
    def __init__(self):
        db = MotorClient(os.environ['MONGOHQ_URL']).rin_stg
        settings = {
            'template_path': str(pathlib.Path(__file__).parent.resolve() / 'template'),
            'static_path': str(pathlib.Path(__file__).parent.resolve() / 'static'),
            # 'debug': True,
            'flickr': flickr.Flickr(os.environ['FLICKR_API_KEY']),
            'cache': flickr.FlickrCache(db)
        }

        handlers = [
            (r'/', MainHandler),
            (r'/page/([1-9][0-9]{0,8})', MainHandler),
        ]
        super().__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self, page="1"):
        page = int(page, 10)
        cache = self.settings['cache']
        result = yield cache.hit(page)

        if not result:
            flick = self.settings['flickr']
            try:
                stat, result = flick.parse((yield flick.fetch(page)))
            except HTTPError as e:
                if e.code == 599: raise tornado.web.HTTPError(408)
                raise
            else:
                if not stat: raise tornado.web.HTTPError(404)
                yield cache.save(result)

        self.render("index.html", photos=result, page=page)

    def render(self, *args, **kwargs):
        self.add_header('X-Content-Type-Options', 'nosniff')
        super().render(*args, **kwargs)

if __name__ == '__main__':
    parse_command_line()
    DogFlickApp().listen(int(os.environ['PORT']))
    tornado.ioloop.IOLoop.instance().start()
