import scrapy
from newsScrape.items import NewsscrapeItem
import datetime
from time import sleep

class ReutersSpider(scrapy.Spider):
    name = "reuters_spider"
    start_urls = [
        "https://www.reuters.com/",
        "https://www.reuters.com/world/",
        "https://www.reuters.com/business/",
        "https://www.reuters.com/markets/",
        "https://www.reuters.com/sustainability/",
        "https://www.reuters.com/legal/",
        "https://www.reuters.com/technology/",
        "https://www.reuters.com/sports/athletics/",
        "https://www.reuters.com/sports/basketball/",
        "https://www.reuters.com/sports/cycling/",
        "https://www.reuters.com/sports/motor-sports/",
        "https://www.reuters.com/sports/nhl/",
        "https://www.reuters.com/sports/tennis/",
        "https://www.reuters.com/sports/baseball/",
        "https://www.reuters.com/sports/cricket/",
        "https://www.reuters.com/sports/golf/",
        "https://www.reuters.com/sports/nfl/",
        "https://www.reuters.com/sports/soccer/",
        "https://www.reuters.com/science/",
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(ReutersSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def parse(self, response):
        # Extract news links from the start page and section links
        news_links = response.css("a.story-title::attr(href)")

        for news_link in news_links:
            yield scrapy.Request(news_link, callback=self.parse_news)
            sleep(2)

        # Follow pagination links
        next_page = response.css("a.pagination-button.next-button::attr(href)").extract_first()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)
            sleep(2)

    def parse_news(self, response):
        # Extract news details
        item = NewsscrapeItem()
        item["title"] = response.css("h1::text").extract_first()
        item["link"] = response.url
        item["content"] = " ".join(response.css("div.ArticleBody_body_2ECha p::text").extract())
        item["provider"] = "Reuters"

        # Extracting the date of publication (adjust the selector based on the actual HTML structure)
        date_str = response.css("time::attr(data-time)").extract_first()
        item["publish_date"] = datetime.datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")

        # Check for duplicate story
        if item["link"] not in self.visited_urls:
            self.visited_urls.add(item["link"])

            # Add other fields as needed

            yield item
