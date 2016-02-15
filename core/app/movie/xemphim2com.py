# -*- coding: utf-8 -*-
from core.function import http_client
from tornado import gen, escape

import sys, traceback

class MovieGeneric(object):
	def __init__(self, link, delay = 3):
		if link:
			if link:
				self.link 	= '/'.join(link.split('/')[:4])
				print(self.link)
		if delay:
			self.delay 	= delay

		self.movie_view_link = None

	@gen.coroutine
	def search(self, text):
		movies 	= []
		try:
			text 	= escape.url_escape(text)
			text 	= 'https://www.google.com.vn/search?q=intitle:"%s"&sitesearch=xemphim2.com&gws_rd=ssl' % text
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
			data 		= data.split('<div class="infomovie">', 1)[1]
			data 		= data.split('<div id="sidebar">',1)[0].split('<div class="tags">',1)[0]
			
			self.movie_view_link = data.split('<a class="link-phim"',1)[1].split('href="',1)[1].split('"',1)[0].strip()
			# poster
			poster 		= data.split('<img src="',1)[1].split('"',1)[0].strip()

			# title
			title 		= data.split(' title="', 1)[1].split('"',1)[0].strip()
			tmp 		= title.split(' - ', 1)
			title 		= tmp[0].strip()
			if len(tmp) > 1:
				subtitle 	= tmp[1].split('(',1)[0].strip()
			else:
				subtitle 	= ""

			# director
			try:
				director 	= [d.strip() for d in data.split('<strong>Đạo diễn: </strong><span>',1)[1].split('</span>')[0].split(',')]
			except:
				director 	= []

			# stars
			stars 		= [d.strip() for d in data.split('<strong>Diễn viên: </strong><span>',1)[1].split('</span>')[0].split(',')]

			# category
			category 	= [d.rsplit(">Phim ", 1)[1].strip() for d in data.split('<strong>Thể loại: </strong>', 1)[1].split('</a></span>',1)[0].split('</a>, <a ')]

			# country
			country 		= data.split('<strong>Quốc gia: </strong>', 1)[1].split('>Phim ',1)[1].split('<',1)[0].strip()

			# length
			length 				= {}
			try:
				tmp 				= data.split('<strong>Thời lượng: </strong><span>', 1)[1].split("</span>",1)[0].strip()
				length['count'] 	= int(tmp.split(' ',1)[0].strip())
				if 'Phút' in tmp:
					length['type'] 	= "short"
				else:
					length['type'] 	= "long"
			except:
				pass
			

			# year
			year 		= data.split('<strong>Năm phát hành: </strong><span>', 1)[1].split("<",1)[0].strip()

			# description
			description 	= data.split('<div class="info-content">',1)[1].strip()
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
			if '/phim/' in self.movie_view_link:
				self.movie_view_link 	= self.movie_view_link.replace('/phim/', '/xem-phim/')
			data 		= yield http_client(self.movie_view_link, c_try=5, c_delay=self.delay)

			servers 	= []
			srvs 		= [data.split('<div class="pagesnumb">',1)[1].split('</li></a></ul></div></div>',1)[0]]
			
			for srv in srvs:
				if not srv.strip():
					continue
				print('servers',srv)
				server 	= {
					"name" : "VIP",
					"movie" : []
				}
				chaps 	= srv.split('</li></a><a id="')
				for chap in chaps:
					name 	= chap.rsplit('<li>',1)[1].strip()
					link 	= chap.split(' href="',1)[1].split('"',1)[0].strip()
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
			data 	= yield http_client(link, c_try=5, c_delay=self.delay)
			data 	= escape.url_unescape(data.split('&proxy.link=',1)[1].split('&',1)[0].strip())
			print(link, data)
			return data
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			return None

