import scrapy
from newsScrape.items import NewsscrapeItem
import datetime
from time import sleep

class ESPNSpider(scrapy.Spider):
    name = "espn_spider"
    start_urls = [
        "https://www.espn.com/",
        "https://www.espn.com/nfl/",
        "https://www.espn.com/college-football/",
        "https://www.espn.com/nba/",
        "https://www.espn.com/nhl/",
        "https://www.espn.com/mlb/",
        "https://www.espn.com/soccer/",
        "https://www.espn.com/mens-college-basketball/",
        "https://www.espn.com/boxing/",
        "https://www.espncricinfo.com/",
        "https://www.espn.com/horse-racing/",
        "https://www.espn.com/racing/nascar/",
        "https://www.espn.com/pll/",
        "https://www.espn.com/wnba/",
        "https://www.espn.com/xfl/",
        "https://www.espn.com/womens-college-basketball/",
        "https://www.espn.com/f1/",
        "https://www.espn.com/little-league-world-series/",
        "https://www.espn.com/nba-g-league/",
        "https://www.espn.com/racing/",
        "https://www.espn.com/rugby/",
        "https://www.espn.com/wwe/",
        "https://www.espn.com/college-sports/",
        "https://www.espn.com/golf/",
        "https://www.espn.com/mma/",
        "https://www.espn.com/olympics/",
        "https://www.espn.com/tennis/",
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(ESPNSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def parse(self, response):
        # Extract news links from the start page and section links
        news_links = response.css("a.realStory::attr(href)")

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
        item["provider"] = "ESPN"

        # Extracting the date of publication (adjust the selector based on the actual HTML structure)
        date_str = response.css("meta[property='article:published_time']::attr(content)").extract_first()
        item["publish_date"] = datetime.datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")

        # Check for duplicate story
        if item["link"] not in self.visited_urls:
            self.visited_urls.add(item["link"])

            # Add other fields as needed

            yield item
