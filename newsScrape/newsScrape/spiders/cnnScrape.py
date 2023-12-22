import scrapy
from newsScrape.items import NewsscrapeItem
import datetime
from time import sleep

class CNNSpider(scrapy.Spider):
    name = "cnn_spider"
    start_urls = [
        "https://www.cnn.com/",
        "https://www.cnn.com/us",
        "https://www.cnn.com/world",
        "https://www.cnn.com/politics",
        "https://www.cnn.com/business",
        "https://www.cnn.com/health",
        "https://www.cnn.com/entertainment",
        "https://www.cnn.com/style",
        "https://www.cnn.com/us/crime-and-justice",
        "https://www.cnn.com/us/energy-and-environment",
        "https://www.cnn.com/weather",
        "https://www.cnn.com/us/space-science",
        "https://www.cnn.com/business/tech",
        "https://www.cnn.com/business/media",
        "https://www.cnn.com/entertainment/movies",
        "https://www.cnn.com/entertainment/tv-shows",
        "https://www.cnn.com/entertainment/celebrities",
        "https://www.cnn.com/sport",
        "https://www.cnn.com/sport/football",
        "https://www.cnn.com/sport/tennis",
        "https://www.cnn.com/sport/golf",
        "https://www.cnn.com/sport/motorsport",
        "https://www.cnn.com/sport/us-sports",
        "https://www.cnn.com/sport/paris-olympics-2024",
        "https://www.cnn.com/sport/climbing",
        "https://www.cnn.com/sport/esports",
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(CNNSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def parse(self, response):
        # Extract news links from the start page and section links
        news_links = response.css("a.card::attr(href)")

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
        item["content"] = " ".join(response.css("div.l-container div div p::text").extract())
        item["provider"] = "CNN"

        # Extracting the date of publication (adjust the selector based on the actual HTML structure)
        date_str = response.css("time::attr(data-time)").extract_first()
        item["publish_date"] = datetime.datetime.fromtimestamp(int(date_str)).strftime("%Y-%m-%d %H:%M:%S")

        # Check for duplicate story
        if item["link"] not in self.visited_urls:
            self.visited_urls.add(item["link"])

            # Add other fields as needed

            yield item
