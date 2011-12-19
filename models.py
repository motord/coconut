# -*- coding: utf-8 -*-
# models

from google.appengine.ext import db
import aetycoon
import hashlib

# Create your models here.
class StaticContent(db.Model):
    body = db.BlobProperty()
    content_type = db.StringProperty(required=True)
    status = db.IntegerProperty(required=True, default=200)
    etag = aetycoon.DerivedProperty(lambda x: hashlib.sha1(x.body).hexdigest())
    headers = db.StringListProperty()
    created=db.DateTimeProperty(auto_now_add=True)
    modified=db.DateTimeProperty(auto_now=True)

class Centipede(db.Model):
    author=db.StringProperty()
    posts=db.IntegerProperty()
    views=db.IntegerProperty()
    pedes=db.ListProperty(item_type=db.Link)
    next=db.LinkProperty()
    created=db.DateTimeProperty(auto_now_add=True)
    modified=db.DateTimeProperty(auto_now=True)

