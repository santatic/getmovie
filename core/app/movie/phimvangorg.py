# -*- coding: utf-8 -*-
from core.function import http_client
from tornado import gen, escape

import sys, traceback

class MovieGeneric(object):
	def __init__(self, link, delay = 3):
		if link:
			if '/xem-phim/' in link:
				link 	= link.replace('/xem-phim/', '/phim/')
			self.link 	= link
		if delay:
			self.delay 	= delay
	
	@gen.coroutine
	def search(self, text):
		movies 	= []
		try:
			text 	= escape.url_escape(text)
			# text 	= "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s&rsz=8&gl=vn" % text
			text 	= 'https://www.google.com.vn/search?q=intitle:"%s"&sitesearch=phimvang.org&gws_rd=ssl' % text
			print(text)

			data 	= yield http_client(text, c_try=5, c_delay=self.delay)
			data 	= data.split('<div id="akp_target"',1)[1].split('<!--m-->',1)[1].rsplit('</div></div></div><!--n--></li></div>',1)[0].split('<!--m-->')

			for m in data:
				link = m.split('href="',1)[1].split('"',1)[0]
				title = m.split('href="',1)[1].split('">',1)[1].split('</a>',1)[0]
				image = ""
				movies.append({
						"link": link,
						"title": title,
						"image": image
					})
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		return movies

	@gen.coroutine
	def get_info(self):
		try:
			data 		= yield http_client(self.link, c_try=5, c_delay=self.delay)
			data 		= data.split('<div class="cover">', 1)[1]
			data 		= data.split('<h4>Liên kết:</h4>',1)[0]
			
			# poster
			data 		= data.split('<p>Tên phim:', 1)
			poster 		= data[0].split('<img src="',1)[1].split('"',1)[0].strip()
			
			# title
			data 		= data[1].split('<p>Đạo diễn:', 1)
			title 		= data[0].split('<span class="fn">',1)[1].split('<',1)[0].strip()
			tmp 		= title.split(' - ', 1)
			title 		= tmp[0].strip()
			subtitle 	= tmp[1].rsplit('(', 1)[0].strip()
			
			# director
			try:
				data 		= data[1].split('<p>Diễn viên:', 1)
				director 	= [data[0].split("title='",1)[1].split("'",1)[0].strip()]
			except:
				traceback.print_exc(file=sys.stdout)
				director 	= ["Đang cập nhật"]
			
			# stars
			data 		= data[1].split('<p>Thể loại:', 1)
			temp 		= data[0].split('</a>')
			stars 		= []
			for tmp in temp:
				tmp 	= tmp.split("title='",1)
				if len(tmp) > 1:
					tmp 	= tmp[1].split("'",1)[0].strip()
					stars.append(tmp)

			# category
			data 		= data[1].split('<p>Quốc gia:', 1)
			temp 		= data[0].split('</a>')
			category 		= []
			for tmp in temp:
				tmp 	= tmp.split("title='",1)
				if len(tmp) > 1:
					tmp 	= tmp[1].split("'",1)[0].strip()
					category.append(tmp)

			# country
			data 		= data[1].split('<p>Thời lượng:', 1)
			country 	= data[0].split("title='",1)[1].split("'", 1)[0]
			
			# length
			length 				= {}
			data 				= data[1].split('<p>Năm sản xuất:', 1)
			tmp 				= data[0].split('<span>',1)[1].split("</span>",1)[0].strip()
			print(tmp)
			length['count'] 	= int(tmp.split(' ',1)[0].strip())
			if 'phút' in tmp:
				length['type'] 	= "short"
			else:
				length['type'] 	= "long"

			# year
			data 		= data[1].split('<p>Đánh giá:', 1)
			year 		= data[0].split('<span>',1)[1].split("</span>",1)[0].strip()

			# description
			data 			= data[1].split('<div class="alt1">Thời lượng:', 1)
			description 	= data[0].split('<div class="entry">',1)[1].split('<p>',1)[1].split('<div class="clear"></div>',1)[0].rsplit('</p>',1)[0].strip()
			description 	= "<p>%s</p>" % description

			###
			response 	= {
				"poster"		: poster,
				"title"			: subtitle, # pass
				"subtitle" 		: title,	# pass
				"director" 		: director,
				"stars" 		: stars,
				"category" 		: category,
				"country" 		: country,
				"length"		: length,
				"year" 			: year,
				"description"	: description
			}
			print(response)
			return response
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	@gen.coroutine
	def get_servers(self):
		try:
			if '/phim/' in self.link:
				link 	= self.link.replace('/phim/', '/xem-phim/')
			data 		= yield http_client(link, c_try=5, c_delay=self.delay)
			servers 	= []
			data 		= data.split('<div id="eps">',1)[1].split('<p class="epi">', 1)[1].split('</div>',1)[0]
			srvs 		= data.split('<p class="epi">')
			
			for srv in srvs:
				name 	= srv.split('<b>- Server ',1)[1].rsplit('</b>', 1)[0]
				if name == "PHIMVÀNG":
					name 	= "VIPER"
				server 	= {
					"name" : name,
					"movie" : []
				}
				chaps_link	= "http://phimvang.org"+srv.split('Xem Full',1)[0].split('<a href="',1)[1].split('"',1)[0]
				chaps_xml 	= chaps_link.replace('.html', '.xml')
				chaps_data 	= yield http_client(chaps_xml, c_try=5, c_delay=self.delay)
				chaps 		= chaps_data.split('<track>',1)[1].rsplit('</track>',1)[0].split('</track>')
				for chap in chaps:
					name 	= chap.rsplit('<title>',1)[1].split('</title>',1)[0]
					link 	= chap.split('<location>',1)[1].split('</location>',1)[0]
					chap 	= {
						"source": [chaps_link, chaps_xml, link],
						"name": name,
					}
					server['movie'].append(chap)
				servers.append(server)
			return servers
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		
	@gen.coroutine
	def get_link(self, link):
		return link

