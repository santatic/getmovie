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
			text 	= 'https://www.google.com.vn/search?q=intitle:"%s"&sitesearch=phimhay365.com&gws_rd=ssl' % text
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
			data 		= data.split('<div class="thumbcontent">', 1)[1]
			data 		= data.split('</div>\n</div>\n</div>\n',1)[0]
			
			# poster
			poster 		= "http://phimhay365.com" + data.split(' src="',1)[1].split('"',1)[0].strip()
			
			# title
			print(data)
			title 		= data.split('<span class="key">Tên Phim:</span>', 1)[1].split('">',1)[1].split('<',1)[0].strip()
			subtitle 	= ""
			

			# director
			try:
				data 		= data.split('<span class="key">Đạo diễn:</span>', 1)
				tmp 		= data[1].split('">',1)[1].split('<',1)[0].strip()
				director 	= [d.strip() for d in tmp.split(',')]
			except:
				traceback.print_exc(file=sys.stdout)
				director 	= ["Đang cập nhật"]

			# stars
			data 		= data[1].split('<span class="key">Diễn viên:</span>', 1)
			tmp 		= data[1].split('">',1)[1].split('<',1)[0].strip()
			stars 		= [d.strip() for d in tmp.split(',')]


			# length
			try:
				length 				= {}
				data 				= data[1].split('<span class="key">Thời Lượng:</span>', 1)
				tmp 				= data[1].split('">',1)[1].split('<',1)[0].strip()
				length['count'] 	= int(tmp.split(' ',1)[0].strip())
				if 'phút' in tmp:
					length['type'] 	= "short"
				else:
					length['type'] 	= "long"
			except:
				length 	= ""
			

			# category
			tmp 		= data[1].split('<span class="key">Thể loại:</span>', 1)
			category 	= [d.rsplit(">", 1)[1].strip() for d in tmp[1].split('</a></span>',1)[0].split('</a>,')]

			# year
			print('\n\n\n', data)
			data 		= data[1].split('Năm Phát Hành:</span>', 1)
			year 		= data[1].split('">',1)[1].split('<',1)[0].strip()
			
			
			# country
			country 	= ""

			# description
			description 	= data[1].split('<div id="gach_ngang" class="box_des">',1)[1].split('</div>',1)[0].strip()
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
			try:
				data 		= data.split('<div class="listserver">',1)[1].split('<span class="name">',1)[1].split('</b></a>&nbsp;</div>',1)[0]
				srvs 		= data.split('<span class="name">')
				
				for srv in srvs:
					if not srv.strip():
						continue

					name 	= srv.split(':</span>',1)[0].strip()

					if 'Picasa' in name:
						name 	= "VIP"
					
					server 	= {
						"name" : name,
						"movie" : []
					}
					chaps 	= srv.split('</b></a>&nbsp;<a ')
					for chap in chaps:
						name 	= chap.rsplit('>',1)[1].strip()
						link 	= chap.split('href="',1)[1].split('"',1)[0].strip()
						chap 	= {
							"source": [link],
							"name": name,
						}
						server['movie'].append(chap)
					servers.append(server)
			except:
				server 	= {
						"name" : "VIP",
						"movie" : [{
							"source": [self.link],
							"name": "Full"
						}]
					}
				servers.append(server)
			
			return servers
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		
	@gen.coroutine
	def get_link(self, link):
		try:
			data 	= yield http_client(link, c_try=5, c_delay=self.delay)
			data 	= escape.url_unescape(data.split('&amp;proxy.link=',1)[1].split('"',1)[0].split('&amp;',1)[0].strip())
			print(link, data)
			return data
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			return None

