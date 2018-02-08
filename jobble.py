#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib import parse
import scrapy
import re
from articlespider.items import JobboleArticleItem
from scrapy.http import Request
from utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['http://blog.jobbole.com/']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    #获取页面的url，并交给scrapy
    def parse(self, response):
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            post_url = post_node.css('::attr(href)').extract_first("")
            img_url = post_node.css("img::attr(src)").extract_first("")
            yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":img_url},callback=self.parse_details,dont_filter=True)

        #提取下一页，并交给scrapy
        next_url = response.css('.next.page-numbers::attr(href)').extract()[0]
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse,dont_filter=True)


    def parse_details(self,response):
        '''提取文章字段'''
        title = response.css('.entry-header h1::text').extract()[0]
        create_data = response.css('.entry-meta-hide-on-mobile').extract()[0]
        sign = re.match('.*?(\d+\/\d+\/\d+).*',create_data, re.S)
        create_time = sign.group(1)
        like_nums = response.css('.btn-bluet-bigger.href-style.bookmark-btn.register-user-only::text').extract()[0]
        like = re.match('.*?(\d+).*',like_nums)
        if like:
            like_num = like.group(1)
        else:
            like_num = None
        comment = response.css('.btn-bluet-bigger.href-style.hide-on-480::text').extract()[0]
        comments = re.match('.*?(\d+).*', comment)
        if comments:
            comment_num = comments.group(1)
        else:
            comment_num = None

        front_image_url = response.meta.get("front_image_url","")
        # 实例化item 对象
        article_item = JobboleArticleItem()
        article_item["title"] = title
        article_item['url'] = response.url
        article_item['url_object_id'] = get_md5(response.url)
        article_item['create_time'] = create_time
        article_item['like_num'] = like_num
        article_item['comment_num'] = comment_num
        article_item['front_image_url'] = [front_image_url]
        yield article_item
