import re
from urllib.parse import quote
import scrapy
from scrapy_redis.spiders import RedisSpider
from SGSearchRedis.items import SearchItem
import redis

connect = redis.Redis(host='127.0.0.1', port=6379, db=15)
keyword_key = 'keyword_key'


class SgSearchSpider(RedisSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'sg_search'
    redis_key = 'sg_search:start_urls'
    allowed_domains = ['sogou.com']
    start_urls = ['https://www.sogou.com/']

    def parse(self, response):
        for x in range(connect.llen(keyword_key)):
            kw = connect.lindex(keyword_key, 0).decode('utf-8').strip()
            connect.lrem(keyword_key, kw)
            print(kw)
            item = SearchItem()
            item['kw'] = kw
            search_url = response.url + 'web?query=%s' % quote(kw)
            print(search_url)
            yield scrapy.Request(url=search_url, callback=self.parse_search, meta={'item': item})

    def parse_search(self, response):
        item = response.meta['item']
        search_nums = response.xpath('//div[@class="search-info"]/p[@class="num-tips"]/text()').extract_first()
        nums = re.compile(r'搜狗已为您找到约(.*?)条相关结果').findall(search_nums)[0]
        item['search_nums'] = nums
        news_url = 'https://news.sogou.com/news?query=%s' % item['kw']
        yield scrapy.Request(url=news_url, callback=self.parse_news, meta={'item': item})

    def parse_news(self, response):
        item = response.meta['item']
        news_nums = response.xpath('//div[@class="header-filt"]/span[@class="filt-result"]/text()').extract_first()
        news = re.compile('找到相关新闻约(.*?)篇').findall(news_nums)[0]
        item['news_nums'] = news
        yield item
