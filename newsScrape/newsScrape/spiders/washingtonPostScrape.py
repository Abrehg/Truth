import scrapy
import datetime
from time import sleep
from newsScrape.items import NewsscrapeItem
import dateparser
from datetime import datetime, timedelta

#scrapy crawl washington_post -o washPost.csv

class WashingtonPostSpider(scrapy.Spider):
    name = 'washington_post'
    start_urls = [
        "https://www.washingtonpost.com/politics/",
        "https://www.washingtonpost.com/business/technology/",
        "https://www.washingtonpost.com/world/",
        "https://www.washingtonpost.com/local/dc/politics/",
        "https://www.washingtonpost.com/local/virginia/politics/",
        "https://www.washingtonpost.com/local/maryland/politics/",
        "https://www.washingtonpost.com/sports/mlb/",
        "https://www.washingtonpost.com/sports/nfl/",
        "https://www.washingtonpost.com/sports/nba/",
        "https://www.washingtonpost.com/sports/colleges/football/",
        "https://www.washingtonpost.com/sports/soccer/",
        "https://www.washingtonpost.com/sports/wnba/",
        "https://www.washingtonpost.com/sports/nhl/",
        "https://www.washingtonpost.com/dc-sports-bog/",
        "https://www.washingtonpost.com/sports/highschools/"
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(WashingtonPostSpider, self).__init__(*args, **kwargs)
        self.visited_urls = self.load_visited_urls()

    def parse(self, response):
        # Extract all the article divs from the main page
        article_divs = response.css('div[data-feature-id="homepage/story"]')

        for article_div in article_divs:
            article_link = article_div.css('a[data-pb-local-content-field="web_headline"]::attr(href)').get()
            if article_link:
                print
                if article_link not in self.visited_urls:
                    self.visited_urls.add(article_link)
                    yield scrapy.Request(url=article_link, callback=self.parse_article)
                else:
                    self.logger.info(f"Duplicate URL encountered: {article_link}")
                sleep(1)

        # Handle "Load More" button, if applicable
        load_more_button = response.css('button.inline-flex.items-center.justify-center.lh-md.overflow-hidden.border-box.min-w-btn.transition-colors.duration-200.ease-in-out.font-sans-serif.font-bold.antialiased.bg-offblack.hover-bg-gray-darker.focus-bg-gray-darker.white.b-solid.bw.bc-transparent.focus-bc-black.brad-lg.pl-md.pr-md.h-md.pt-0.pb-0.w-100.pointer')
        if load_more_button:
            formdata = {'form_key': 'load_more_key'}  # Add any necessary form data

            yield scrapy.FormRequest(
                url=response.url,
                method='POST',
                formdata=formdata,
                callback=self.parse,
                dont_filter=True  # Important to avoid ignoring duplicates
            )
            sleep(1)

    def parse_article(self, response):
        item = NewsscrapeItem()

        # Extract data from the article page
        title = response.css('h3[data-qa="card-title"]::text').get()
    
        # Extracting the date of publication
        publication_date_str = response.css('span.wpds-c-iKQyrV::text').get()

        # Parse the relative time using dateparser
        publication_date = dateparser.parse(publication_date_str)

        # If the parsed date is relative, adjust it to be close to the current local time
        if publication_date and publication_date_str.lower() in ['just now', 'a moment ago', '1 minute ago', 'a minute ago']:
            # If the publication date is recent, set it close to the local time
            adjusted_date = datetime.now() - timedelta(minutes=1)
        elif publication_date:
            # If the date is not relative, use the parsed date
            adjusted_date = publication_date
        else:
            # If the date parsing fails, set a default or handle it as needed
            adjusted_date = datetime.now()

        # Extracting content from the teaser div
        teaser_div = response.css('div.teaser-content.grid-center')
        teaser_content = ' '.join(teaser_div.css('div.wpds-c-PJLV.article-body p::text').extract())

        # Extracting additional content from subsequent divs
        additional_content_divs = response.css('div.wpds-c-PJLV.article-body:not(.teaser-content) p::text')
        additional_content = ' '.join(additional_content_divs.extract())

        # Combine the teaser content and additional content
        content = teaser_content + ' ' + additional_content

        item["title"] = title
        item["link"] = response.url
        item["content"] = content
        item["provider"] = "Washington Post"

        # Set the adjusted timestamp to the item
        item["publish_date"] = adjusted_date.strftime("%Y-%m-%d %H:%M:%S")

        yield item
    
    def save_visited_urls(self):
        with open('visited_urls_Wash.txt', 'w') as file:
            file.write('\n'.join(self.visited_urls))

    def close(self, reason):
        self.save_visited_urls()
        super().close(reason)

    def load_visited_urls(self):
        try:
            with open('visited_urls_Wash.txt', 'r') as file:
                return set(file.read().splitlines())
        except FileNotFoundError:
            return set()
