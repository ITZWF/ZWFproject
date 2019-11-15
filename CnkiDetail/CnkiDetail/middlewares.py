# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import re

from scrapy import signals

from my_tools.ip_test import IpTest


class RandMiddleware(object):

    def __init__(self):
        self.ip_test = IpTest()
        self.connect = self.ip_test.connect
        self.proxy_key = self.ip_test.proxy_key
        self.ua_ls = self.ip_test.ua_list()

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.ua_ls))
        ip_ls = [self.connect.lindex(self.proxy_key, i).decode('utf-8') for i in
                 range(self.connect.llen(self.proxy_key))]
        print(len(ip_ls))
        if len(ip_ls) < 3:
            self.ip_test.get_ip()
        ip = random.choice(ip_ls)
        [proxy_host, proxy_port] = re.compile(r'http://(.*?):(\d+)').findall(ip)[0]
        if not self.ip_test.test_ip(proxy_host, proxy_port):
            self.ip_test.del_ip('http://' + proxy_host + ':' + proxy_port)
        else:
            request.meta['proxy'] = ip
        return None

    def process_response(self, request, response, spider):
        if '信息提示' in response.text:
            self.ip_test.del_ip(request.meta['proxy'])
            return request.replace(url=response.url, dont_filter=True)
        else:
            return response


class CnkidetailSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CnkidetailDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
