# -*- coding: utf-8 -*-
# __author__ = 'peter'

from string import Template
import scrapemark

url_template=Template('http://www.tianya.cn/new/publicforum/articleslist.asp?pageno=${pageno}&stritem=develop')
threshold=1000
encoding='gbk'
HTTP_DATE_FMT = '%Y-%m-%d %H:%M:%S'

def threads():
    tyjj=(url_template.substitute(pageno=str(i)) for i in range(2, 0, -1))
    for url in tyjj:
        for thread in scrapemark.scrape("""
            {*
            <table name=''>
            <tr><td><a href='{{ [threads].url }}'></a></td>
            <td><a>{{ [threads].author }}</a></td>
            <td>{{ [threads].views }}</td>
            <td>{{ [threads].posts }}</td>
            <td></td>
            </table>
            *}
            """, url=url)['threads']:
            yield thread

def crawl():
    hot=[{'url':thread['url'], 'author':thread['author'], 'posts':int(thread['posts']), 'views':int(thread['views'])} for thread in threads() if int(thread['posts'])>threshold]
    return hot

def pages():
    d={}
    urls=[]
    url='http://www.tianya.cn/publicforum/content/develop/1/359777.shtml'
    pages=scrapemark.scrape("""
        <div class="pages" id="pageDivTop">
        {*
        <a href="{{ [pages] }}"></a>
        *}
        <span></span>
        </div>
        """, url=url)['pages'][:-1]
    for page in pages:
        d[page]=1
    urls=[url]
    urls.extend(d.keys()[:-2])
    return urls

def process():
    url='http://www.tianya.cn/publicforum/content/develop/1/905898.shtml'
    template=Template(u"""
        {*
        <table id="firstAuthor">
		    <tr>
                <td>
                    <a>${author}</a> &nbsp;发表日期：{{ [stanzas].datetime }}
		        </td>
		    </tr>
	    </table>
	    <div id="pContentDiv">
	        <div class="post">
	        {{ [stanzas].content }}
	        </div>
	    </div>
        *}
        {*
        <table>
		    <tr>
                <td>
                    <a>${author}</a>　回复日期：{{ [stanzas].datetime }}
		        </td>
		    </tr>
	    </table>
        <div class="post">
        {{ [stanzas].content }}
        </div>
        *}
    """)
    pattern=template.substitute(author=u'flp713')
    pattern=scrapemark.compile(pattern)
    stanzas=scrapemark.scrape(pattern, url=url, encoding=encoding)['stanzas']
    return stanzas


if __name__ == '__main__':
    process()
#    crawl()