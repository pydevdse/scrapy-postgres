import logging
import sys
import datetime
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lxml import html
from ..items import PythonAuthorItem, PythonPostItem, PythonReleaseItem

class PythonSpider(scrapy.Spider): # (CrawlSpider): #
    name = "releases"
    #allowed_domains = ['blog.python.org']
    start_urls = ['https://blog.python.org/']
    COUNT_PAGES = 2

    def start_requests(self):
        urls = [
            'https://blog.python.org/',
            ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_posts)

    """
    def parse(self, response, **kwargs):
        if self.COUNT_PAGES > 0:
            self.COUNT_PAGES -= 1
            print('COUNT PAGES:', self.COUNT_PAGES)
            next_page = response.xpath('.//a[@class="blog-pager-older-link"]/@href').extract_first()
            print('NEXT PAGE URL:', next_page)
            if next_page:
                yield response.follow(url=next_page, callback=self.parse_posts) 
    """
    def parse_posts(self, response):
        posts = response.xpath('//div[@class="date-outer"]')
        for post in posts:
            release_urls = [url for url in post.xpath('.//div[@class="post-body entry-content"]//a/@href').extract()
                            if '/downloads/release/' in url]
            text = post.xpath('.//text()').extract()
            text_page = ''
            for t in text:
                if ('Get it here' in t) or ('http' in t):
                    continue
                text_page += t
            date_post = post.xpath('.//div[@class="post-footer"]//span[@class="post-timestamp"]/a/abbr/@title').extract_first().split('T')[0]
            date_post = date_post.split('-')
            date_post = datetime.date(int(date_post[0]), int(date_post[1]), int(date_post[2]))

            post = {
                'url': post.xpath('.//h3[@class="post-title entry-title"]/a/@href').extract_first(),
                'date': date_post,
                'title': post.xpath('.//h3[@class="post-title entry-title"]/a/text()').get(),
                'author': post.xpath('.//span/span[@class="fn"]/text()').extract_first(),
                'text': text_page,
                'releases_urls': release_urls,
            }
            """
            author_item = PythonAuthorItem()
            author_item['author'] = post['author']
            yield author_item
            
            post_item = PythonPostItem()
            post_item['url'] = post['url']
            post_item['date'] = post['date']
            post_item['title'] = post['title']
            post_item['author'] = post['author']
            post_item['text'] = post['text']
            #yield post_item
            """
            meta = response.meta
            meta['post'] = post
            
            for release in release_urls:
                yield response.follow(url=release, callback=self.parse_page_release, meta=meta)

        if self.COUNT_PAGES > 1:
            self.COUNT_PAGES -= 1
            print('COUNT PAGES:', self.COUNT_PAGES)
            next_page = response.xpath('.//a[@class="blog-pager-older-link"]/@href').extract_first()
            print('NEXT PAGE URL:', next_page)
            if next_page:
                yield response.follow(url=next_page, callback=self.parse_posts)
    
    def parse_page_release(self, response):
        def table_parse(table):
            table_release=[]
            for line in table:
                l = line.xpath('.//td')
                if not l or len(l) < 5:
                    print('TABLE LINE NOT FOUND:', line.text)
                    continue
                try:
                    version = l[0].xpath('./a/text()')[0]
                except Exception as e:
                    print('ERROR', e)
                    print('Field "Version" in line table not found, please contact developer')
                    version = None
                try:
                    url_tgz = l[0].xpath('./a/@href')[0]
                except Exception as e:
                    print('ERROR', e)
                    print('Field "Href" in line table not found, please contact developer')
                    url_tgz = None
                try:
                    oper_syst = l[1].xpath('./text()')[0]
                except Exception as e:
                    print('ERROR', e)
                    print('Field "Operating System" in line table not found, please contact developer')
                    oper_syst = None
                try:
                    description = l[2].xpath('./text()')[0]
                except Exception as e:
                    print(e)
                    description = ''
                    print('Field "Description" in line table not found, please contact developer')
                try:
                    md5_sum = l[3].xpath('./text()')[0]
                except Exception as e:
                    print('ERROR', e)
                    print('Field "md5 sum" in line table not found, please contact developer')
                    md5_sum = None
                try:
                    file_size = l[4].xpath('./text()')[0]
                except Exception as e:
                    print('ERROR', e)
                    print('Field "file size" in line table not found, please contact developer')
                    file_size = None

                table_release.append({
                    'version':version,
                    'url_tgz':url_tgz,
                    'oper_syst':oper_syst,
                    'description':description,
                    'md5_sum':md5_sum,
                    'file_size':file_size
                })
            return table_release

        post = response.meta['post']
        #logging.info(f'Post: {post}')
        tree = html.fromstring(response.text)
        title = response.xpath('.//meta[@property="og:title"]/@content').get()
        h1 = response.xpath('.//h1[@class="page-title"]/text()').get()
        date_release = response.xpath('.//article[@class="text"]/p/text()').extract_first()
        pep_urls = [u for u in response.xpath('.//@href').extract() if 'peps/pep' in u]
        text = tree.xpath('.//article[@class="text"]')[0]
        text_article = ''
        for t in text.findall('*'):
            if t.tag == 'ul':
                ul = t.xpath('.//li//text()')
                ul_text = ''
                for u in ul:
                    ul_text += u
                text_article += ul_text+'\n'
                continue
            te = t.xpath('.//text()')
            if not te:
                continue
            if t.tag == 'header' and 'Files' in te:
                break
            text_p = ''
            for te_p in te:
                text_p += te_p
            text_article += text_p+'\n'
        table = tree.xpath('.//table/tbody/tr')
        table_release = table_parse(table)
        release = {
            'title': title,
            'h1': h1,
            'date': date_release,
            'urls_pep': pep_urls,
            'text_release': text_article,
            'table_release': table_release
            }
        releases_item = PythonReleaseItem()
        releases_item['post'] = post
        releases_item['title'] = release['title']
        releases_item['h1'] = release['h1']
        releases_item['url'] = response.url
        releases_item['date'] = release['date']
        releases_item['urls_pep'] = release['urls_pep']
        releases_item['text_release'] = release['text_release']
        releases_item['table_release'] = {'table_files': release['table_release']}
        yield releases_item



