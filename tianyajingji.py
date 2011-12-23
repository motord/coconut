# -*- coding: utf-8 -*-
# __author__ = 'peter'

from models import Centipede, StaticContent, Stanza
import scrapemark
import logging
from google.appengine.api import memcache
from mapreduce import operation as op
from google.appengine.api import urlfetch
from google.appengine.api import images
from google.appengine.ext import deferred, db
import urlparse
from google.appengine.ext import deferred
import mechanize
import re, itertools
from string import Template
from bottle import template
import bottle

url_template=Template('http://www.tianya.cn/new/publicforum/articleslist.asp?pageno=${pageno}&stritem=develop')
threshold=1000
encoding='gb18030'
bottle.TEMPLATE_PATH.insert(0, './templates/')

def threads():
    tyjj=(url_template.substitute(pageno=str(i)) for i in range(10, 0, -1))
    for url in tyjj:
        for thread in scrapemark.scrape("""
        {*
        <table name=''>
        <tr><td><a href='{{ [threads].url }}'>{{ [threads].title}}</a></td>
        <td><a>{{ [threads].author }}</a></td>
        <td>{{ [threads].views|int }}</td>
	    <td>{{ [threads].posts|int }}</td>
	    <td></td>
	    </table>
        *}
        """, url=url, encoding=encoding)['threads']:
            yield thread

def crawl():
    hot=({'url':thread['url'], 'author':thread['author'], 'title': thread['title'], 'posts':thread['posts'], 'views':thread['views'], 'stanzas':{}} for thread in threads() if thread['posts']>threshold)
    for thread in hot:
        deferred.defer(process, thread)

def process(thread):
    for url in pages(thread):
        stanza_template=Template(u"""
        {*
        <table>
		    <tr align="center">
                <td align="center">
                    <a>${author}</a> &nbsp;发表日期：{{ [stanzas].datetime }}
		        </td>
		</tr>
	    </table>
        *}
        """)
        logging.info(thread['author'])
        pattern=scrapemark.compile(stanza_template.substitute(author=thread['author']))
        logging.info(pattern)
        thread['stanzas'][url]=scrapemark.scrape(pattern, url=url, encoding=encoding)['stanzas']
        logging.info(thread['stanzas'][url])

def new_stanzas(thread, centipede):
    for url, stanzas in thread['stanzas'].items():
        for stanza in stanzas:
            yield Stanza(parent=centipede, page_url=url, content=stanza['datetime'])

def pages(thread):
    centipede=Centipede.get_by_key_name(thread['url'])
    d={}
    urls=[]
    logging.info(thread['url'])
    for page in scrapemark.scrape("""
        <div class="pages" id="pageDivTop">
        {*
        <a href="{{ [pages] }}"></a>
        *}
        <span></span>
        </div>
        """, url=thread['url'])['pages'][:-1]:
        d[page]=1
    if centipede is None:
        centipede=Centipede(key_name=thread['url'], species=db.Category(u'天涯经济'), author=thread['author'], title=thread['title'], posts=thread['posts'], views=thread['views'], pedes=[])
        urls=[db.Link(thread['url'])]
        urls.extend([db.Link(key) for key in d.keys()[:-2]])
    else:
        urls=[db.Link(centipede.next)]
        urls.extend([db.Link(url) for url in d.keys()[:-2] if url not in centipede.pedes])
    logging.info(urls)
    centipede.pedes.extend(urls)
    centipede.next=db.Link(d.keys()[-2])
    for url in urls:
        yield url
    centipede.put()
    centipede_url_components=urlparse.urlparse(thread['url'])
    centipede_url_netloc_path=centipede_url_components.netloc + centipede_url_components.path
    content=StaticContent.get_by_key_name(centipede_url_netloc_path)
    stanzas=[stanza for stanza in new_stanzas(thread, centipede)]
    if content is None:
        content=StaticContent(key_name=centipede_url_netloc_path, template=db.Text(template('centipede.html', centipede=centipede, stanzas=stanzas, template_next=True)), content_type='text/html')
    else:
        content.template=db.Text(template(content.template, centipede=centipede, stanzas=stanzas, template_next=True))
    db.put(stanzas)
    content.put()
    memcache.delete(content.key().name())
