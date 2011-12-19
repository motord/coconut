# -*- coding: utf-8 -*-
# __author__ = 'peter'

from google.appengine.ext import deferred, db
import tianyajingji
from mapreduce import base_handler, mapreduce_pipeline
from bottle import debug, Bottle
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from models import StaticContent
import logging
import tianyajingji

debug(True)
app=Bottle()

#@cron_only
@app.get('/bots/crawl')
def crawl():
    deferred.defer(tianyajingji.crawl)

@app.get('/bots/done')
def regenerate():
    logging.info('regenerating site')
    contents=['index.html']
    memcache.delete_multi(contents)
    try:
        db.delete(StaticContent.get_by_key_name(contents))
    except Exception, err:
            pass

def main():
    util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
