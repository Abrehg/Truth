import scrapy
from newsScrape.items import NewsscrapeItem
import datetime
from time import sleep

class CBSSpider(scrapy.Spider):
    name = "cbs_spider"
    start_urls = [
        "https://www.cbsnews.com/",
        "https://www.cbsnews.com/us/",
        "https://www.cbsnews.com/world/",
        "https://www.cbsnews.com/politics/",
        "https://www.cbsnews.com/entertainment/",
        "https://www.cbsnews.com/healthwatch/",
        "https://www.cbsnews.com/moneywatch/",
        "https://www.cbsnews.com/technology/",
        "https://www.cbsnews.com/science/",
        "https://www.cbsnews.com/crime/",
        "https://www.cbssports.com/",
        "https://www.cbssports.com/nfl/",
        "https://www.cbssports.com/college-football/",
        "https://www.cbssports.com/college-basketball/",
        "https://www.cbssports.com/nba/",
        "https://www.cbssports.com/golf/",
        "https://www.cbssports.com/soccer/",
        "https://www.cbssports.com/mlb/",
        "https://www.cbssports.com/nhl/",
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(CBSSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def parse(self, response):
        # Extract news links from the start page and section links
        news_links = response.css("a.item__title::attr(href)")

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
        item["title"] = response.css("h1.title::text").extract_first()
        item["link"] = response.url
        item["content"] = " ".join(response.css("div.content__body p::text").extract())
        item["provider"] = "CBS"

        # Extracting the date of publication (adjust the selector based on the actual HTML structure)
        date_str = response.css("time::attr(data-time-published)").extract_first()
        item["publish_date"] = datetime.datetime.utcfromtimestamp(int(date_str)).strftime("%Y-%m-%d %H:%M:%S")

        # Check for duplicate story
        if item["link"] not in self.visited_urls:
            self.visited_urls.add(item["link"])

            # Add other fields as needed

            yield item
