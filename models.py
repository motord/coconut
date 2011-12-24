# -*- coding: utf-8 -*-
# models

from google.appengine.ext import db
import aetycoon
import hashlib

# Create your models here.
class StaticContent(db.Model):
    template = db.TextProperty()
    body = db.BlobProperty()
    content_type = db.StringProperty(required=True)
    status = db.IntegerProperty(required=True, default=200)
    etag = aetycoon.DerivedProperty(lambda x: hashlib.sha1(x.template.encode('utf8') if x.template else x.body).hexdigest())
    headers = db.StringListProperty()
    created=db.DateTimeProperty(auto_now_add=True)
    modified=db.DateTimeProperty(auto_now=True)

class Centipede(db.Model):
    species=db.CategoryProperty()
    author=db.StringProperty()
    title=db.StringProperty()
    comments=db.IntegerProperty()
    views=db.IntegerProperty()
    pedes=db.ListProperty(item_type=db.Link)
    next=db.LinkProperty()
    created=db.DateTimeProperty(auto_now_add=True)
    modified=db.DateTimeProperty(auto_now=True)

class Stanza(db.Model):
    page_url=db.LinkProperty()
    published=db.DateTimeProperty()
    content=db.TextProperty()
    created=db.DateTimeProperty(auto_now_add=True)
