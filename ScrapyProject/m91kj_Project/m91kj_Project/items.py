# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class M91KjProjectItem(scrapy.Item):
    # define the fields for your item here like:
    Title = scrapy.Field()
    Score = scrapy.Field()
    Year = scrapy.Field()
    Region = scrapy.Field()
    Type = scrapy.Field()
    Detail_url = scrapy.Field()
    pass
