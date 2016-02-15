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
			text 	= "http://phimtructuyenhd.com/search.php?q=%s&limit=20" % text
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
			data 		= data.split('<div class="blockbody">', 1)[1]
			data 		= data.split('<div class="tags">',1)[0]
			
			# poster
			poster 		= "http://phimtructuyenhd.com/" + data.split('<img class="thumb" src="',1)[1].split('"',1)[0].strip()

			# title
			title 		= data.split(' title="', 1)[1].split('"',1)[0].strip()
			tmp 		= title.split(' - ', 1)
			title 		= tmp[0].strip()
			if len(tmp) > 1:
				subtitle 	= tmp[1].strip()
			else:
				subtitle 	= ""

			# year
			year 		= data.split('<span class="year">(', 1)[1].split(')</span>',1)[0].strip()

			# director
			try:
				director 	= [d.rsplit(">",1)[1].strip() for d in data.split('<dt>Đạo diễn:</dt>', 1)[1].split('</a></dd>',1)[0].split('</a> ,<a')]
			except:
				traceback.print_exc(file=sys.stdout)
				director 	= []

			# stars
			stars 		= [d.rsplit(">",1)[1].strip() for d in data.split('<dt>Diễn viên:</dt>', 1)[1].split('</a></dd>',1)[0].split('</a> ,<a')]



			# category
			category 		= [d.rsplit(">",1)[1].strip() for d in data.split('<dt>Thể loại:</dt>', 1)[1].split('</a></dd>',1)[0].split('</a> ,<a')]

			
			# country
			country 		= data.split('<dt>Quốc gia:</dt><dd>', 1)[1].split("</dd>",1)[0].strip()

			# length
			length 				= {}
			tmp 				= data.split('<dt>Thời lượng:</dt><dd>', 1)[1].split("</dd>",1)[0].strip()
			length['count'] 	= tmp.split(' ',1)[0].strip()
			if '/' in length['count']:
				length['count'] = length['count'].split('/',1)[1].strip()
			length['count'] 	= int(length['count'])
			if 'Phút' in tmp:
				length['type'] 	= "short"
			else:
				length['type'] 	= "long"

			
			# description
			description 	= data.split(' id="info-film">',1)[1].rsplit('</div>',2)[0].strip()
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
				self.link 	= self.link.replace('/phim/', '/xem-phim/')
			data 		= yield http_client(self.link, c_try=5, c_delay=self.delay)

			servers 	= []
			data 		= data.split("<div class='label'>",1)[1].rsplit('</li></ul><br /></span>',1)[0]
			srvs 		= data.split("<div class='label'>")
			
			for srv in srvs:
				if not srv.strip():
					continue
				print('servers',srv)
				name 	= srv.split("<img src=",1)[1].split(">",1)[1].split(':<',1)[0].strip()

				if 'Picasa' in name:
					name 	= "VIP"
				server 	= {
					"name" : name,
					"movie" : []
				}
				chaps 	= srv.rsplit('</a>', 1)[0].split('</a><a id="')
				for chap in chaps:
					name 	= chap.rsplit('">',1)[1].strip()
					link 	= chap.split('href="',1)[1].split('"',1)[0].strip()
					url 	= "http://phimtructuyenhd.com/xml/%s.xml" % chap.split('onclick="setupplayer(',1)[1].split(',',1)[0].strip()

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

