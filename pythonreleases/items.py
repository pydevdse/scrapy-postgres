# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class PythonAuthorItem(Item):
    author = Field()


class PythonPostItem(Item):
    url = Field()
    date = Field()
    title = Field()
    author = Field()
    releases_urls = Field()
    text = Field()


class PythonReleaseItem(Item):
    post = Field()
    title = Field()
    h1 = Field()
    url = Field()
    date = Field()
    urls_pep = Field()
    text_release = Field()
    table_release = Field()
