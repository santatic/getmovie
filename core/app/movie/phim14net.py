# -*- coding: utf-8 -*-
from . import filmDecrypter
from core.function import http_client
from tornado import gen

import sys, traceback

key = 'j2gn4pjn41hgy5z2wi5g'

class MovieGeneric(object):
	def __init__(self, link, delay = 3):
		if '/xem-phim/' in link:
			link 	= link.replace('/xem-phim/', '/phim/')
		self.link 	= link
		if delay:
			self.delay 	= delay

	@gen.coroutine
	def get_info(self):
		try:
			data 		= yield http_client(self.link, c_try=5, c_delay=self.delay)
			data 		= data.split('<div class="intro">', 2)[1].split('</div><!--/.block-->',1)[0]
			
			# poster
			data 		= data.split('<div class="info">', 2)
			poster 		= data[0].split(' src="',2)[1].split('"',1)[0].strip()
			
			# title
			data 		= data[1].split('<div class="alt1">Đạo diễn', 2)
			title 		= data[0].split('color="white">',2)[1].split('<',1)[0].strip()
			tmp 		= title.split(' - ', 1)
			title 		= tmp[0]
			subtitle 	= tmp[1].rsplit(' ', 1)[0]
			
			# director
			data 		= data[1].split('<div class="alt2">Diễn viên', 2)
			director 	= [data[0].split('title="',2)[1].split('"',1)[0].strip()]

			# stars
			data 		= data[1].split('<div class="alt1">Thể loại', 2)
			temp 		= data[0].split('</a>,')
			stars 		= []
			for tmp in temp:
				tmp 	= tmp.split('title="',2)[1].split('"',1)[0].strip()
				stars.append(tmp)

			# category
			data 		= data[1].split('<div class="alt2">Quốc Gia', 2)
			temp 		= data[0].split('</a>,')
			category 		= []
			for tmp in temp:
				tmp 	= tmp.split('title="',2)[1].split('"',1)[0].strip()
				category.append(tmp)

			# country
			data 		= data[1].split('<div class="alt1">Thời lượng:', 2)
			country 	= data[0].split('title="Xem Phim ',2)[1].split('"', 1)[0]
			
			# length
			data 		= data[1].split('<div class="alt2">Năm phát hành:', 2)
			length 		= data[0].split('</div>',1)[0].strip()

			# year
			data 		= data[1].split('<div class="alt1">Lượt xem:', 2)
			year 		= data[0].split('title="Phim ',2)[1].split('"', 1)[0].strip()


			# descript_long
			data 			= data[1].split('<div class="alt1">Thời lượng:', 2)
			descript_long 	= data[0].split('<div class="description">',2)[1].split('<div class="message">',2)[1].split('<div class="title hr"><span>Trailer:',1)[0].rsplit('</div>',1)[0].strip()

			response 	= {
				"poster"		: poster,
				"title" 		: title,
				"subtitle"		: subtitle,
				"director" 		: director,
				"stars" 		: stars,
				"category" 		: category,
				"country" 		: country,
				"length"		: length,
				"year" 			: year,
				"descript_long"	: descript_long
			}
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
			data 		= data.split('<ul id="server_list">',1)[1].split('</div>',1)[0].split('<li class="server_item">', 1)[1]
			srvs 		= data.split('<li class="server_item">')
			
			for srv in srvs:
				name 	= srv.split(': </strong>',1)[0].rsplit('>', 1)[1]
				server 	= {
					"name" : name,
					"movie" : []
				}
				chaps = srv.split('<li class="active">',1)
				if len(chaps) == 2:
					chaps 	= chaps[1].rsplit('</a>', 1)[0].split('</a>')
				else:
					chaps = srv.split('<li class="">',1)[1].rsplit('</a>', 1)[0].split('</a>')
			
				for chp in chaps:
					link 	= chp.split('href="',1)[1].split('"',1)[0]
					name 	= chp.rsplit('>',1)[1]
					chap 	= {
						"source": [link],
						"name": name
					}
					server['movie'].append(chap)
				servers.append(server)
			return servers
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		
	@gen.coroutine
	def get_link(self, link):
		try:
			data 		= yield http_client(link, c_try=5, c_delay=self.delay)
			data 		= data.split('<param name="FlashVars" value="', 1)[1].split('>',1)[0]
			data 		= data.split('proxy.link=phim14*',2)[1].split('&', 1)[0]

			cryptor 	= filmDecrypter.filmDecrypter(198,128)
			movie 		= cryptor.decrypt(data, key,'ECB').split('\0')[0]
			return movie
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			return None
