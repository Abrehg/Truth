import scrapy
from newsScrape.items import NewsscrapeItem
import datetime
from time import sleep

class APNewsSpider(scrapy.Spider):
    name = "apnews_spider"
    start_urls = [
        "https://apnews.com/",
        "https://apnews.com/world-news",
        "https://apnews.com/us-news",
        "https://apnews.com/politics",
        "https://apnews.com/sports",
        "https://apnews.com/entertainment",
        "https://apnews.com/hub/nfl",
        "https://apnews.com/hub/mlb",
        "https://apnews.com/hub/nhl",
        "https://apnews.com/hub/nba",
        "https://apnews.com/hub/wnba-basketball",
        "https://apnews.com/hub/auto-racing",
        "https://apnews.com/hub/soccer",
        "https://apnews.com/hub/tennis",
        "https://apnews.com/hub/golf",
        "https://apnews.com/hub/television",
        "https://apnews.com/hub/music",
        "https://apnews.com/business",
        "https://apnews.com/science",
        "https://apnews.com/health",
        "https://apnews.com/climate-and-environment",
        "https://apnews.com/technology",
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(APNewsSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def parse(self, response):
        # Extract news links from the start page and section links
        news_links = response.css("a.CardHeadline-headlineLink::attr(href)")

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
        item["content"] = " ".join(response.css("div.Article div p::text").extract())
        item["provider"] = "AP News"

        # Extracting the date of publication (adjust the selector based on the actual HTML structure)
        date_str = response.css("time::attr(data-time)").extract_first()
        item["publish_date"] = datetime.datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")

        # Check for duplicate story
        if item["link"] not in self.visited_urls:
            self.visited_urls.add(item["link"])

            # Add other fields as needed

            yield item
