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
			text 	= 'https://www.google.com.vn/search?q=intitle:"%s"&sitesearch=phimhd.vn&gws_rd=ssl' % text
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
			data 		= data.split('<!-- container --><script>',1)[0]
			
			# poster
			poster 		= data.split('<img src="',1)[1].split('"',1)[0].strip()
			
			# title
			data 		= data.split('<p>Tên phim:', 1)
			title 		= data[1].split('<span class="fn">',1)[1].split('<',1)[0].strip()
			tmp 		= title.split(' - ', 1)
			title 		= tmp[0].strip()
			subtitle 	= tmp[1].rsplit(' - ', 1)[0].strip()
			
			# director
			try:
				data 		= data[1].split('<p>Đạo diễn:', 1)
				director 	= [data[1].split('">',1)[1].split("</a>",1)[0].strip()]
			except:
				traceback.print_exc(file=sys.stdout)
				director 	= ["Đang cập nhật"]
			
			# stars
			data 		= data[1].split('<p>Diễn viên:', 1)
			temp 		= data[1].split('</span></p>',1)[0].split('</a>')
			stars 		= []
			for tmp in temp:
				tmp 	= tmp.split('">',1)
				if len(tmp) > 1:
					tmp 	= tmp[1].split("</a>",1)[0].strip()
					stars.append(tmp)

			# category
			data 		= data[1].split('<p>Thể loại:', 1)
			temp 		= data[1].split('</span></p>',1)[0].split('</a>')
			category 		= []
			for tmp in temp:
				tmp 	= tmp.split('">',1)
				if len(tmp) > 1:
					tmp 	= tmp[1].split("</a>",1)[0].strip()
					category.append(tmp)

			# country
			data 		= data[1].split('<p>Quốc gia:', 1)
			country 	= data[1].split('">',1)[1].split("</a>",1)[0].strip()
			
			# length
			length 				= {}
			data 				= data[1].split('<p>Thời lượng:', 1)
			tmp 				= data[1].split('<span>',1)[1].split("</span>",1)[0].strip()
			length['count'] 	= int(tmp.split(' ',1)[0].strip())
			if 'phút' in tmp.lower():
				length['type'] 	= "short"
			else:
				length['type'] 	= "long"

			try:
				imdb  	= float(data[1].split('<span class="average">',1)[1].split('<',1)[0])
				if imdb == 9.5:
					imdb = 0
			except:
				imdb 	= 0

			# year
			data 		= data[1].split('<p>Năm phát hành:', 1)
			year 		= data[1].split('">',1)[1].split("</a>",1)[0].strip()

			# description
			description 	= data[1].split('<div class="entry">',1)[1].split('<div class="clear"></div>',1)[0].rsplit('</div>',1)[0].strip()
			if '<p style="text-align: justify;">' in description:
				description = description.split('<p style="text-align: justify;">',1)[1].rsplit('</p>',1)[0].strip();
			###
			try:
				image = [x.split('"',1)[0] for x in description.split('<img src="',1)[1].rsplit('" alt=""/>',1)[0].split('<img src="')]
			except:
				image = []


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
				"imdb" 			: imdb,
				"image"			: image,
				"description"	: description
			}
			# print(response)
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
				if '<b>Download phim:</b>' in srv:
					continue

				name 	= srv.split('<b>',1)[1].split('</b>', 1)[0]
				if 'Danh sách tập' in name:
					name 	= "VIPER"
				server 	= {
					"name" : name,
					"movie" : []
				}
				
				chaps 	= srv.split('</b>', 1)[1].split('</p>', 1)[0].rsplit('</a>',1)[0].split('</a>')
				for chap in chaps:
					print(chap)
					name 	= chap.rsplit('">',1)[1].strip()
					link 	= "http://phimhd.vn" + chap.split(' href="',1)[1].split('"',1)[0]
					chap 	= {
						"source": [link],
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

