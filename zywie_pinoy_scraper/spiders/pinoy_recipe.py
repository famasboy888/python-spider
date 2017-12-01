# -*- coding: utf-8 -*-
import scrapy
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from time import sleep

class PinoyRecipeSpider(scrapy.Spider):
    name = 'pinoy_recipe'
    allowed_domains = ['panlasangpinoy.com']
    start_urls = ['http://panlasangpinoy.com/indexes/recipe-index/']
    ################################################################
    cred = credentials.Certificate('service.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL' : 'https://zywie-2b7c2.firebaseio.com'
    })
    rootDB = db.reference()

    def parse(self, response):
        links = response.css('li.ei-item > h3 > a::attr(href)').extract()
        categories = response.css('li.ei-item > h3 > a::text').extract()

        for category_id, link in zip(categories, links):
            link = response.urljoin(link)
            if db.reference('food_index_category').child(category_id).get():
                print('Data is already inside')
            else:
                self.rootDB.child('food_index_category').child(category_id).update({
                    'food_index_category_link': link
                })
                request = scrapy.Request(link, callback=self.subcat)
                request.meta['category'] = category_id
                yield request
        pass

    def subcat(self, response):
        links = response.css('li.ei-item > h4.ei-item-title > a::attr(href)').extract()
        food_titles = response.css('li.ei-item > h4.ei-item-title > a::text').extract()

        for food_title, link in zip(food_titles, links):
            link = response.urljoin(link)
            request = scrapy.Request(link, callback=self.getDetails)
            request.meta['title_id'] = food_title
            request.meta['category'] = response.meta['category']
            request.meta['link'] = link
            yield request
        pass

    def getDetails(self, response):
        name_food = response.css('header.entry-header > h1::text').extract_first()
        list_recipe = response.css('li.ingredient::text').extract()
        description = response.css('div.entry-content > p::text').extract_first()
        if db.reference('food_title').child(response.meta['title_id']).get():
            print('Data is already inside')
        else:
            self.rootDB.child('food_title').child(response.meta['title_id']).update({
                'category_id': response.meta['category'],
                'link': response.meta['link'],
                'name_food': response.meta['title_id'],
                'list_recipe': list_recipe,
                'description': description
            })
        pass
