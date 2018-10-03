from scrapy import Spider, Request
from billboardcatalog.items import BillboardcatalogItem
from datetime import date as datefunc, datetime, timedelta
import re

class catalogSpider(Spider):
	name = 'catalog_spider'
	allowed_urls = ['https://www.billboard.com/']
	start_urls = ['https://www.billboard.com/charts/catalog-albums/1991-05-25']

	def parse(self, response):

		# calculate how many weeks between 1991-05-25 and next saturday to current day
		start = datetime(1991,5,25).date()
		end=datefunc.today()
		#we know it will take any end date and round forward to the nearest saturday
		# this is ROUNDED DOWN so we add 1, and 2 if today is saturday
		if (end-start).days%7==0:
			weeks = ((end-start).days//7)+1
		else:
			weeks = ((end-start).days//7)+2
		# write an iterator to create all the dates given the number of weeks.
		# QUESTION: can I make this more efficient? Making 2 lists (dates & urls), any way to make just 1?
		dates=[]
		for i in range(weeks):
			dates.append(start+timedelta(days=7*i))

		# reminder of how list comprehension works: [output expression FOR iterator variable IN iterable]
		result_urls = ['https://www.billboard.com/charts/catalog-albums/{}'.format(str(x)) for x in dates]
		for url in result_urls:
			date = re.split('\/', url)[-1]
			yield Request(url=url, meta = {'date': date}, callback=self.parse_week_page)

	def parse_week_page(self, response):
		# for 1 on the chart
		date = [response.meta['date']]*50
		rank = []
		rank.append(1)
		album = []
		album.append(response.xpath("//div[@class='chart-number-one__title']/text()").extract_first())
		artist = []
		artist.append(response.xpath("//div[@class='chart-number-one__artist']/a/text()").extract_first().strip('\n'))
		# charts 2-50:
		records = response.xpath("//div[@class='chart-list-item  ']")
		for record in records:
			rank+=record.xpath("@data-rank").extract()
			album+=record.xpath("@data-title").extract()
			artist+=record.xpath("@data-artist").extract()
	
		for i in range(len(rank)):
			# print(date[i],rank[i],album[i],artist[i])
			item = BillboardcatalogItem()
			item['date']= date[i]
			item['rank']=rank[i]
			item['album']=album[i]
			item['artist']=artist[i]
			yield item

		# OLD METHOD:
		# records = response.xpath("//div[@class='chart-list-item__first-row']")
		# for record in records:
			# rank is not good. alternative idea...can just add 2 to incrementor? below:
			# rank = record+2   # if record doesn't refer to the incrementor, maybe enumerate?
			# rank = record.xpath("//div[@class='chart-list-item__rank']/text()").extract_first()
			# album is good
			# album = record.xpath("//span[@class='chart-list-item__title-text']/text()").extract_first()
			# ARTIST
			# below works IF THERE IS A LINK
			# artist = response.xpath("//div[@class='chart-list-item__artist']/a/text()").extract()
			# the below will return the name IF THERE IS NO LINK, otherwise will return '\n' or '\n '
			# artist = record.xpath("//div[@class='chart-list-item__artist']/text()").extract_first()
			# so i need a condition to check if there is a link