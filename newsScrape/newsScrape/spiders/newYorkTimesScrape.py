import scrapy
import datetime
from time import sleep
from newsScrape.items import NewsscrapeItem
import dateparser
from datetime import datetime, timedelta

#scrapy crawl ny_times -o ny_times.csv

class NYTimesSpider(scrapy.Spider):
    name = 'ny_times'

    handle_httpstatus_list = [403]

    existing_start_urls = [
        "https://www.nytimes.com/section/us",
        "https://www.nytimes.com/section/business",
        "https://www.nytimes.com/section/technology",
        "https://www.nytimes.com/section/technology/personaltech",
        "https://www.nytimes.com/section/business/economy",
        "https://www.nytimes.com/section/business/media",
        "https://www.nytimes.com/section/your-money",
        "https://www.nytimes.com/section/arts",
        "https://www.nytimes.com/spotlight/lifestyle",
        "https://www.nytimes.com/section/sports"
    ]
    dynamic_start_urls = []
    #https://www.nytimes.com/issue/todayspaper/2018/01/02/todays-new-york-times
    #start_date = datetime(2018, 1, 1)
    #end_date = datetime.now()
    #date_range = [datetime(2018, 1, 1) + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    #dynamic_start_urls = [
    #    f"https://www.nytimes.com/issue/todayspaper/{date.strftime('%Y/%m/%d')}/todays-new-york-times" for date in date_range
    #]

    start_urls = existing_start_urls + dynamic_start_urls

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, *args, **kwargs):
        super(NYTimesSpider, self).__init__(*args, **kwargs)
        self.visited_urls = self.load_visited_urls()
        self.page_number = 1 

    def parse(self, response):
        # Extract all the article divs from the main page
        article_divs = response.css('li.css-18yolpw')

        for article_div in article_divs:
            # Extract the link URL from the anchor within the div
            article_link = article_div.css('a.css-8hzhxf::attr(href)').get()

            if article_link:
                article_link = scrapy.http.TextResponse(response.url).urljoin(article_link)  # Convert to absolute URL
                if article_link not in self.visited_urls:
                    print(article_link)
                    self.visited_urls.add(article_link)
                    # Follow the link and parse the corresponding article
                    yield scrapy.Request(url=article_link, callback=self.parse_article)
                    sleep(1)
                else:
                    self.logger.info(f"Duplicate URL encountered: {article_link}")

        # Extract additional links if they exist
        additional_links = response.css('li.css-i435f0 a::attr(href)').extract()
        self.follow_additional_links(additional_links, response.url)

        additional_links = response.css('a.css-1u3p7j1::attr(href)').extract()
        self.follow_additional_links(additional_links, response.url)

        # Handle "Load More" button, if applicable
        self.page_number += 1

        # Formdata for pagification
        formdata = {
            'form_key': 'load_more_key',
            'page': str(self.page_number)
        }

        if self.page_number <= 10:
            yield scrapy.FormRequest(
                url=response.url,
                method='POST',
                formdata=formdata,
                callback=self.parse,
                meta={'dont_merge_cookies': True},  # Important for maintaining cookies across requests
                dont_filter=True  # Important to avoid ignoring duplicates
            )
            sleep(1)

    def follow_additional_links(self, additional_links, base_url):
        for additional_link in additional_links:
            additional_link = scrapy.http.TextResponse(base_url).urljoin(additional_link)  # Convert to absolute URL
            if additional_link and additional_link not in self.visited_urls:
                print(additional_link)
                self.visited_urls.add(additional_link)
                # Follow the additional link and parse the corresponding article
                yield scrapy.Request(url=additional_link, callback=self.parse_article)
                sleep(1)
            else:
                self.logger.info(f"Duplicate URL encountered or link is missing: {additional_link}")

    def parse_article(self, response):
        self.logger.info(f"Scraping article: {response.url}")
        
        try:
            item = NewsscrapeItem()

            # Extract data from the article page
            title = response.css('div.css-1vkm6nb h1.css-1l8buln::text').get()
    
            # Extracting the date of publication
            publication_date_str = response.css('div[data-testid="reading-time-module"] time::attr(datetime)').get()
            print(type(publication_date_str))

            # Parse the relative time using dateparser
            if publication_date_str and isinstance(publication_date_str, str):
                try:
                    # Parse the publication date
                    publication_date = dateparser.parse(publication_date_str)\

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
                except Exception as e:
                    self.logger.error(f"Error parsing publication date: {str(e)}")
            else:
                self.logger.warning("Publication date is not a valid string.")
            
            all_content_elements = response.css('p.css-at9mc1.evys1bk0, p.css-at9mc1.evys1bk0 a::text').extract()

            # Joining the content elements into a single string
            content = ''.join(response.xpath('//div[@class="css-s99gbd StoryBodyCompanionColumn"]//p[@class="css-at9mc1 evys1bk0"]//text()').getall())

            item["title"] = title
            item["link"] = response.url
            item["content"] = content
            item["provider"] = "The New York Times"

            # Set the adjusted timestamp to the item
            item["publish_date"] = adjusted_date.strftime("%Y-%m-%d %H:%M:%S")

            yield item
        except Exception as e:
            self.logger.error(f"Error parsing article: {str(e)}")

    def save_visited_urls(self):
        with open('visited_urls_NYT.txt', 'w') as file:
            file.write('\n'.join(self.visited_urls))

    def close(self, reason):
        self.logger.info(f"Spider closed: {reason}")
        self.save_visited_urls()
        super(NYTimesSpider, self).close(reason)

    def load_visited_urls(self):
        try:
            with open('visited_urls_NYT.txt', 'r') as file:
                return set(file.read().splitlines())
        except FileNotFoundError:
            return set()
        