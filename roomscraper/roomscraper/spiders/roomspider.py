import scrapy
from roomscraper.items import RoomItem

class RoomSpider(scrapy.Spider):
    name = "roomspider"
    allowed_domains = ["www.bayut.com"]
    start_urls = ["https://www.bayut.com/to-rent/property/dubai/"]

    def parse(self, response):
        rooms = response.css('article.ca2f5674')

        for room in rooms:
            next_page = room.css('a').attrib['href']
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse_room_page)

        next_page = response.css('a.b7880daf[title="Next"]::attr(href)').get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)

    def parse_room_page(self, response):
        
        price_currency = response.css('.c4fc20ba span.e63a6bfb::text').get()
        price_amount = response.css('.c4fc20ba span._105b8a67::text').get()
        
        beds_text = response.css('div._6f6bb3bc span[aria-label="Beds"] span.fc2d1086::text').get()
        beds = int(beds_text.split()[0]) if beds_text else None
        baths_text = response.css('div._6f6bb3bc span[aria-label="Baths"] span.fc2d1086::text').get()
        baths = int(baths_text.split()[0]) if baths_text else None
        area = response.css('div._6f6bb3bc span[aria-label="Area"] span.fc2d1086 span::text').get()
        
        nav_items = response.xpath('//div[@class="_8468d109"]//a//text()').getall()
        breadcrumbs = " > ".join(nav_items)

        amenities = response.css('div._208d68ae span._005a682a::text').getall()
        all_text_result = list(map(str, amenities)) if amenities else None

        
        room_item = RoomItem()
        
        room_item['property_id'] = response.css('li ._812aa185[aria-label="Reference"]::text').get()
        room_item['purpose'] = response.css('li ._812aa185[aria-label="Purpose"]::text').get()
        room_item['type'] = response.css('li ._812aa185[aria-label="Type"]::text').get()
        room_item['added_on'] = response.css('li ._812aa185[aria-label="Reactivated date"]::text').get()
        room_item['furnishing'] = response.css('li ._812aa185[aria-label="Furnishing"]::text').get()       
        room_item['price'] = {
            'currency': price_currency,
            'amount': price_amount,
        }
        room_item['location']  = response.css('div._1f0f1758::text').get()       
        room_item['bed_bath_size'] = {
            'bedrooms': beds,
            'bathrooms': baths,
            'size': area,
        }
        room_item['agent_name'] = response.css('span._63b62ff2 .f730f8e6::text').get()
        room_item['image_url'] = response.css('img.bea951ad::attr(src)').get()
        room_item['breadcrumbs']  = breadcrumbs
        room_item['amenities']  = all_text_result
        room_item['description']  = response.css('span._2a806e1e').xpath('string()').get()
        
        yield room_item
