# -*- coding: utf-8 -*-
# __author__ = 'peter'

from models import Centipede, StaticContent
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

url_template=Template('http://www.tianya.cn/new/publicforum/articleslist.asp?pageno=${pageno}&stritem=develop')
threshold=1000

def threads():
    tyjj=(url_template.substitute(pageno=str(i)) for i in range(10, 0, -1))
    for url in tyjj:
        for thread in scrapemark.scrape("""
        {*
        <table name=''>
        <tr><td><a href='{{ [threads].url }}'></a></td>
        <td><a>{{ [threads].author }}</a></td>
        <td>{{ [threads].views|int }}</td>
	    <td>{{ [threads].posts|int }}</td>
	    <td></td>
	    </table>
        *}
        """, url=url)['threads']:
            yield thread

def crawl():
    hot=({'url':thread['url'], 'author':thread['author'], 'posts':thread['posts'], 'views':thread['views'], 'stanzas':{}} for thread in threads() if thread['posts']>threshold)
    for thread in hot:
        deferred.defer(process, thread)

def process(thread):
    for url in pages(thread):
        template=Template("""
        {*
        <table>
		    <tr align="center">
                <td align="center">
                    <a>${author}</a>{{ [stanzas].datetime }}
		        </td>
		</tr>
	    </table>
        *}
        """)
        logging.info(thread['author'])
        pattern=template.substitute(author=thread['author'])
        logging.info(pattern)
        thread['stanzas'][url]=scrapemark.scrape(pattern, url=thread['url'])['stanzas']
        logging.info(thread['stanzas'][url])
        content=StaticContent.get_by_key_name(thread['url'])
        stanzas=list(itertools.chain.from_iterable(thread['stanzas'].values()))
        if content is None:
            content=StaticContent(key_name=thread['url'], template=str(template('centipede.html', template_next=True)), content_type='text/html')
        else:

            content.template=str(template(content.template, stanzas=stanzas, template_next=True))
        content.put()

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
        centipede=Centipede(key_name=thread['url'], author=thread['author'], posts=thread['posts'], views=thread['views'], pedes=[])
        urls=[db.Link(centipede.key().name())]
        urls.extend([db.Link(key) for key in d.keys()[:-2]])
    else:
        centipede.pedes.extend()
        urls=[db.Link(centipede.next)]
        urls.extend([db.Link(url) for url in d.keys()[:-2] if url not in centipede.pedes])
    logging.info(urls)
    centipede.pedes.extend(urls)
    centipede.next=db.Link(d.keys()[-2])
    for url in urls:
        yield url
    centipede.put()