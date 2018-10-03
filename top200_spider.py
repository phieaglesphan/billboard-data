from scrapy import Spider, Request
from billboard200.items import Billboard200Item
from datetime import date as datefunc, datetime, timedelta
import re

class top200Spider(Spider):
	name = 'top200_spider'
	allowed_urls = ['https://www.billboard.com/']
	start_urls = ['https://www.billboard.com/charts/billboard-200/1963-08-17']

	def parse(self, response):
		start = datetime(1963,8,17).date()
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

		result_urls = ['https://www.billboard.com/charts/billboard-200/{}'.format(str(x)) for x in dates]
		for url in result_urls:
			date = re.split('\/', url)[-1]
			yield Request(url=url, meta = {'date': date}, callback=self.parse_week_page)

	def parse_week_page(self, response):
		# for 1 on the chart
		date = [response.meta['date']]*200
		rank = []
		rank.append(1)
		album = []
		album.append(response.xpath('//div[@class="chart-number-one__title"]/text()').extract_first())
		artist = []
		artist.append(response.xpath('//div[@class="chart-number-one__artist"]/a/text()').extract_first().strip('\n'))
		#charts 2-50
		records = response.xpath("//div[@class='chart-list-item  ']")
		for record in records:
			rank+=record.xpath("@data-rank").extract()
			album+=record.xpath("@data-title").extract()
			artist+=record.xpath("@data-artist").extract()

		for i in range(len(rank)):
			item = Billboard200Item()
			item['date']= date[i]
			item['rank']=rank[i]
			item['album']=album[i]
			item['artist']=artist[i]
			yield item