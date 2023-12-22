import scrapy
from newsScrape.items import NewsscrapeItem
import datetime
from time import sleep

class FoxNewsSpider(scrapy.Spider):
    name = "fox_spider"
    start_urls = [
        "https://www.foxnews.com/",
        "https://www.foxnews.com/us",
        "https://www.foxnews.com/politics",
        "https://www.foxnews.com/world",
        "https://www.foxnews.com/media",
        "https://www.foxnews.com/entertainment",
        "https://www.foxnews.com/sports",
        "https://www.foxnews.com/category/sports/nfl",
        "https://www.foxnews.com/category/sports/ncaa-fb",
        "https://www.foxnews.com/category/sports/mlb",
        "https://www.foxnews.com/category/sports/nba",
        "https://www.foxnews.com/category/sports/nhl",
        "https://www.foxnews.com/category/auto/nascar",
        "https://www.foxnews.com/category/sports/ufc",
        "https://www.foxnews.com/category/sports/golf",
        "https://www.foxnews.com/category/sports/tennis",
        "https://www.foxnews.com/category/sports/ncaa-bk",
        "https://www.foxnews.com/category/sports/soccer",
        "https://www.foxnews.com/category/sports/pro-wrestling",
        "https://www.foxnews.com/lifestyle",
        "https://www.foxnews.com/category/tech/artificial-intelligence",
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(FoxNewsSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def parse(self, response):
        # Extract news links from the start page and section links
        news_links = response.css("a.article") + response.css("a.title")

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
        item["content"] = " ".join(response.css("div.article-body p::text").extract())
        item["provider"] = "Fox News"

        # Extracting the date of publication (adjust the selector based on the actual HTML structure)
        date_str = response.css("time.date::attr(data-time-published)").extract_first()
        item["publish_date"] = datetime.datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")

        # Check for duplicate story
        if item["link"] not in self.visited_urls:
            self.visited_urls.add(item["link"])

            # Add other fields as needed

            yield item
