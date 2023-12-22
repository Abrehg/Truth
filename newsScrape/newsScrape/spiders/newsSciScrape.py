import scrapy
from newsScrape.items import NewsscrapeItem
import datetime
from time import sleep

class NewScientistSpider(scrapy.Spider):
    name = "newscientist_spider"
    start_urls = [
        "https://www.newscientist.com/",
        "https://www.newscientist.com/subject/health/",
        "https://www.newscientist.com/subject/space/",
        "https://www.newscientist.com/subject/physics/",
        "https://www.newscientist.com/subject/technology/",
        "https://www.newscientist.com/subject/environment/",
        "https://www.newscientist.com/subject/mind/",
        "https://www.newscientist.com/subject/humans/",
        "https://www.newscientist.com/subject/life/",
        "https://www.newscientist.com/subject/mathematics/",
        "https://www.newscientist.com/subject/chemistry/",
        "https://www.newscientist.com/subject/earth/",
        "https://www.newscientist.com/subject/society/",
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(NewScientistSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def parse(self, response):
        # Extract news links from the start page and section links
        news_links = response.css("a.card-link::attr(href)")

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
        item["content"] = " ".join(response.css("div.article-body-text p::text").extract())
        item["provider"] = "New Scientist"

        # Extracting the date of publication (adjust the selector based on the actual HTML structure)
        date_str = response.css("time::attr(data-time-published)").extract_first()
        item["publish_date"] = datetime.datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")

        # Check for duplicate story
        if item["link"] not in self.visited_urls:
            self.visited_urls.add(item["link"])

            # Add other fields as needed

            yield item