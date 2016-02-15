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
			text 	= "http://movie.vndailys.com/search.php?q=%s&limit=20" % text
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
			data 		= data.split('<div class="info-movie">', 1)[1]
			data 		= data.split('<div class="bg-main info-movie-contents">',1)[0]
			
			self.movie_view_link = data.split('<div class="play">',1)[1].split('href="',1)[1].split('"',1)[0].strip()
			# poster
			poster 		= data.split('<img src="',1)[1].split('"',1)[0].strip()
			
			# trailer
			try:
				trailer 	= [data.split('<a class="xem-trailer"',1)[1].split('rel="',1)[1].split('"',1)[0].strip()]
			except:
				trailer 	= ""

			# title
			title 		= data.split(' title="', 1)[1].split('"',1)[0].strip()
			tmp 		= title.split(' - ', 1)
			title 		= tmp[0].strip()
			if len(tmp) > 1:
				subtitle 	= tmp[1].strip()
			else:
				subtitle 	= ""
			
			# category
			data 		= data.split('<p><span>Thể loại:</span>', 1)
			category 	= [d.rsplit(">", 1)[1].strip() for d in data[1].split('</a></p>',1)[0].split('</a>,')]

			# director
			try:
				data 		= data.split('<p><span>Đạo diễn:</span>', 1)
				director 	= [d.rsplit(">",1)[1].strip() for d in data[1].split('</a></p>',1)[0].split('</a>')]
			except:
				traceback.print_exc(file=sys.stdout)
				director 	= ["Đang cập nhật"]
			
			# stars
			data 		= data[1].split('<p><span>Diễn viên:</span>', 1)
			stars 		= [d.rsplit(">",1)[1].strip() for d in data[1].split('</a></p>',1)[0].split('</a>')]

			
			# year
			data 		= data[1].split('<p><span>Năm phát hành:</span>', 1)
			year 		= data[1].split("</p>",1)[0].strip()
			
			# length
			length 				= {}
			data 				= data[1].split('<p><span>Thời lượng:</span>', 1)
			tmp 				= data[1].split("</p>",1)[0].strip()
			length['count'] 	= int(tmp.split(' ',1)[0].strip())
			if 'phút' in tmp:
				length['type'] 	= "short"
			else:
				length['type'] 	= "long"

			# country
			data 		= data[1].split('<p><span>Quốc gia:</span>', 1)
			country 	= data[1].split("</p>",1)[0].strip()

			# description
			description 	= data[1].split('<div class="lbox icontents">',1)[1].split('</div>',1)[0].strip()
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
			data 		= data.split('<div class="eplist" id="_listep">',1)[1].split('</span></p></div>',1)[0]
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
		try:
			link 	= "http://movie.vndailys.com/xml/%s.xml" % link.rsplit('/m',1)[1].split('.',1)[0].strip()
			data 	= yield http_client(link, c_try=5, c_delay=self.delay)
			data 	= data.split('</title><location>',1)[1].split('</location>',1)[0].strip()
			print(link, data)
			return data
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			return None

