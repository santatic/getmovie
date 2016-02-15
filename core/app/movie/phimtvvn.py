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

		self.movie_view_link = None
	@gen.coroutine
	def search(self, text):
		movies 	= []
		try:
			text 	= escape.url_escape(text)
			text 	= "http://phimtv.vn/search.php?q=%s&limit=20" % text
			data 	= yield http_client(text, c_try=5, c_delay=self.delay)
			data 	= data.split('</a></li>',1)[1].rsplit('</a></li>',1)[0].split('</a></li>')
			movies 	= []
			for m in data:
				link = m.split('<a href="',1)[1].split('"',1)[0]
				title = ' - '.join(m.split('<strong>',1)[1].split('<br ',1)[0].split('</strong><br>'))
				image = 'http://phimtv.vn/' + m.split('src="',1)[1].split('"',1)[0]
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
			data 		= data.split('<div class="khung-img">', 1)[1]
			data 		= data.split('<div class="bg-main info-movie-contents">',1)[0]
			
			self.movie_view_link = data.split('<a class="xemphim"',1)[1].split(' href="',1)[1].split('"',1)[0].strip()
			# poster
			poster 		= "http://phimtv.vn/" + data.split('src="',1)[1].split('"',1)[0].strip()
			
			# trailer
			try:
				trailer 	= [data.split('class="trailer" ',1)[1].split('rel="',1)[1].split('"',1)[0].strip()]
			except:
				trailer 	= ""

			# title
			title 		= data.split('<img alt="', 1)[1].split('"',1)[0].strip()
			tmp 		= title.split(' - ', 1)
			title 		= tmp[0].strip()
			if len(tmp) > 1:
				subtitle 	= tmp[1].strip()
			else:
				subtitle 	= ""
			
			# director
			try:
				director 	= [d.rsplit(">",1)[1].strip() for d in data.split('<h3>Đạo diễn</h3>:', 1)[1].split('</a><br',1)[0].split('</a>, <a')]
			except:
				traceback.print_exc(file=sys.stdout)
				director 	= []
			
			# stars
			stars 		= [d.rsplit(">",1)[1].strip() for d in data.split('<h3>Diễn viên</h3>:', 1)[1].split('</a><br',1)[0].split('</a>, <a')]

			# country
			country 	= data.split('<h3>Quốc gia</h3>:',1)[1].split('<strong>',1)[1].split("</strong>",1)[0].strip()

			# category
			category 	=  [d.rsplit(">",1)[1].strip() for d in data.split('<h3>Thể loại</h3>:', 1)[1].split('</a><br',1)[0].split('</a>, <a')]

			
			
			# year
			year 		=  data.split('<h3>Năm sản xuất</h3>:',1)[1].split('>',1)[1].split("<",1)[0].strip()
			
			# length
			length 				= {}
			tmp 				= data.split('<h4>Thời lượng</h4>:',1)[1].split('>',1)[1].split("<",1)[0].strip()
			length['count'] 	= int(tmp.split(' ',1)[0].strip())
			if 'phút' in tmp:
				length['type'] 	= "short"
			else:
				length['type'] 	= "long"

			
			# description
			description 	= data.split('<div class="content-info">',1)[1].split('<div class="trailer-info">',1)[0].strip()
			###
			response 	= {
				"poster"		: poster,
				"title"			: subtitle, # pass
				"subtitle" 		: title,	# pass
				"trailer" 		: trailer,
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
			if '/phim/' in self.movie_view_link:
				self.movie_view_link 	= self.movie_view_link.replace('/phim/', '/xem-phim/')
			data 		= yield http_client(self.movie_view_link, c_try=5, c_delay=self.delay)

			servers 	= []
			data 		= data.split('<div class="eplist" id="_listep">',1)[1].rsplit('</span><br />',1)[0]
			srvs 		= data.split('</span><br />')
			
			for srv in srvs:
				if not srv.strip():
					continue
				print('servers',srv)
				name 	= srv.split("<span class='svname'>",1)[1].split(':</span>',1)[0].strip()
				if 'SV ' in name:
					name = name.split('SV ',1)[1].strip()
				if 'Picasaweb' in name:
					name 	= "VIP"
				server 	= {
					"name" : name,
					"movie" : []
				}
				chaps 	= srv.split("<span class='svep'>", 1)[1].rsplit('</a>', 1)[0].split('</a><a id="')
				for chap in chaps:
					name 	= chap.rsplit('">',1)[1].strip()
					link 	= chap.split('href="',1)[1].split('"',1)[0].strip()
					url 	= "http://phimtv.vn/xml/%s.xml" % chap.split('setupplayer(',1)[1].split(',',1)[0].strip()
					chap 	= {
						"source": [link, url],
						"name": name,
					}
					server['movie'].append(chap)
				servers.append(server)
			return servers
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		
	@gen.coroutine
	def get_link(self, link):
		try:
			data 	= yield http_client(link, c_try=5, c_delay=self.delay)
			data 	= data.split('</title><location>',1)[1].split('</location>',1)[0].strip()
			print(link, data)
			return data
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			return None

