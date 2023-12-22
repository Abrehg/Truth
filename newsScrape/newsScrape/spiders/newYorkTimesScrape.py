import scrapy
from newsScrape.items import NewsscrapeItem
import datetime
from time import sleep

class NYTimesSpider(scrapy.Spider):
    name = "ny_times"
    start_urls = [
        "https://www.nytimes.com/",
        "https://www.nytimes.com/section/us",
        "https://www.nytimes.com/section/business",
        "https://www.nytimes.com/section/technology",
        "https://www.nytimes.com/section/technology/personaltech",
        "https://www.nytimes.com/section/business/economy",
        "https://www.nytimes.com/section/business/media",
        "https://www.nytimes.com/section/your-money",
        "https://www.nytimes.com/section/arts",
        "https://www.nytimes.com/spotlight/lifestyle",
        "https://www.nytimes.com/section/sports",
        "https://theathletic.com/",
        "https://theathletic.com/nfl/",
        "https://theathletic.com/mlb/",
        "https://theathletic.com/nba/",
        "https://theathletic.com/college-football/",
        "https://theathletic.com/nhl/",
        "https://theathletic.com/college-basketball/",
        "https://theathletic.com/fantasy/football/",
        "https://theathletic.com/golf/",
        "https://theathletic.com/football/mls/",
        "https://theathletic.com/sports-business/",
        "https://theathletic.com/mma/",
        "https://theathletic.com/motorsports/",
        "https://theathletic.com/boxing/",
        "https://theathletic.com/sports-betting/",
        "https://theathletic.com/fantasy/baseball/",
        "https://theathletic.com/fantasy/basketball/",
        "https://theathletic.com/football/nwsl/",
        "https://theathletic.com/wnba/",
        "https://theathletic.com/culture/"
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(NYTimesSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def parse(self, response):
        # Extract news links from the start page and section links
        news_links = response.css("a[href*='/202']/@href").extract()

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
        item["content"] = " ".join(response.css("p.css-1g7m0tk::text").extract())
        item["provider"] = "The New York Times"

        # Extracting the date of publication (adjust the selector based on the actual HTML structure)
        date_str = response.css("time.css-1g9dxnu::attr(data-time)").extract_first()
        item["publish_date"] = datetime.datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")

        # Check for duplicate story
        if item["link"] not in self.visited_urls:
            self.visited_urls.add(item["link"])

            yield item
