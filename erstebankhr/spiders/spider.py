import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import ErstebankhrItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.erstebank.hr/bin/erstegroup/gemesgapi/feature/gem_site_hr_www-erstebank-hr-hr-gradjanstvo-es7/,"

base_payload = "{\"filter\":[{\"key\":\"path\",\"value\":\"/content/sites/hr/ebc/www_erstebank_hr/hr/press/priopcenja" \
               "-za-medije\"},{\"key\":\"tags\",\"value\":\"hr:ebc/press/priopcenja-za-medije," \
               "hr:ebc/press/priopcenja-za-medije/financijska-izvjesca," \
               "hr:ebc/press/priopcenja-za-medije/Kadrovske-promjene," \
               "hr:ebc/press/priopcenja-za-medije/komentari-i-analize,hr:ebc/press/priopcenja-za-medije/ostalo," \
               "hr:ebc/press/priopcenja-za-medije/proizvodi-i-usluge," \
               "hr:ebc/press/priopcenja-za-medije/Sponzorstva-i-donacije\"}],\"page\":%s,\"query\":\"*\",\"items\":5," \
               "\"sort\":\"DATE_RELEVANCE\",\"requiredFields\":[{\"fields\":[\"teasers.NEWS_DEFAULT\"," \
               "\"teasers.NEWS_ARCHIVE\",\"teasers.newsArchive\"]}]} "
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
  'Content-Type': 'application/json',
  'Accept': '*/*',
  'Origin': 'https://www.erstebank.hr',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.erstebank.hr/hr/press/priopcenja-za-medije',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'TCPID=12131115832624980424; 3cf5c10c8e62ed6f6f7394262fadd5c2=ffb311b6d6c2f7e071b7c1a53fef5c06; TC_PRIVACY=0@024@3%2C4@2@1615802290150%2C1615802290150%2C1649498290150@; TC_PRIVACY_CENTER=3%2C4; _ga=GA1.2.874875980.1615802290; _gid=GA1.2.1637738303.1615802290; _cs_c=1; _fbp=fb.1.1615802290725.1589974652; WRIgnore=true; _gat_UA-54243800-1=1; _cs_cvars=%7B%221%22%3A%5B%22Page%20Name%22%2C%22priopcenja-za-medije%22%5D%2C%222%22%3A%5B%22Page%20Title%22%2C%22Priop%C4%87enja%20za%20medije%22%5D%2C%223%22%3A%5B%22Page%20Template%22%2C%22standardContentPage%22%5D%2C%224%22%3A%5B%22Language%22%2C%22hr_hr%22%5D%7D; _cs_id=50781fb3-a9f3-acb1-be66-99a1b4d56272.1615802291.1.1615802356.1615802291.1.1649966291184.Lax.0; _cs_s=3.1; __CT_Data=gpv=3&ckp=tld&dm=erstebank.hr&apv_53_www56=3&cpv_53_www56=3'
}



class ErstebankhrSpider(scrapy.Spider):
	name = 'erstebankhr'
	start_urls = ['https://www.erstebank.hr/hr/press/priopcenja-za-medije']
	page = 0

	def parse(self, response):
		payload = base_payload % self.page
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = json.loads(data.text)
		for post in raw_data['hits']['hits']:
			link = post['_source']['url']
			date = post['_source']['date']
			title = post['_source']['title']
			yield response.follow(link, self.parse_post, cb_kwargs={'date': date, 'title': title})
		if self.page < raw_data['hits']['total'] // 5:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response, date, title):
		description = response.xpath(
			'(//div[@class="w-auto mw-full rte"])[position()>3]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=ErstebankhrItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
