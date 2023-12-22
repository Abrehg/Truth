import scrapy
import datetime
from time import sleep
from newsScrape.items import NewsscrapeItem

class WashingtonPostSpider(scrapy.Spider):
    name = "washington_post"
    start_urls = [
        "https://www.washingtonpost.com/",
        "https://www.washingtonpost.com/politics/",
        "https://www.washingtonpost.com/business/technology/",
        "https://www.washingtonpost.com/world/",
        "https://www.washingtonpost.com/local/?%20va.",
        "https://www.washingtonpost.com/sports/"
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(WashingtonPostSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def parse(self, response):
        # Extract news links from the start page and section links
        news_links = response.css("a[data-pb-field='headlines.basic']::attr(href)").extract()

        for news_link in news_links:
            yield scrapy.Request(news_link, callback=self.parse_news)
            sleep(2)

        # Follow pagination links
        next_page = response.css("a[data-pb-field='pagination.next']::attr(href)").extract_first()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)
            sleep(2)

    def parse_news(self, response):
        # Extract news details
        item = NewsscrapeItem()
        item["title"] = response.css("h1::text").extract_first()
        item["link"] = response.url
        item["content"] = " ".join(response.css("div.article-body p::text").extract())
        item["provider"] = "Washington Post"
        
        # Extracting the date of publication (adjust the selector based on the actual HTML structure)
        date_str = response.css("meta[itemprop='datePublished']::attr(content)").extract_first()
        item["publish_date"] = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")

        # Check for duplicate story
        if item["link"] not in self.visited_urls:
            self.visited_urls.add(item["link"])
            
            # Add other fields as needed

            yield item


