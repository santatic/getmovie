# -*- coding: utf-8 -*-
from core.function import http_client
from tornado import gen, escape

import sys, traceback

class MovieGeneric(object):
	def __init__(self, link, delay = 3):
		if link:
			if '/Phim-view.aspx' in link:
				link 	= link.replace('/Phim-view.aspx', '/Phim-ct.aspx')
			self.link 	= link
		if delay:
			self.delay 	= delay

		self.movie_data = None
	@gen.coroutine
	def search(self, text):
		movies 	= []
		try:
			text 	= escape.url_escape(text)
			# text 	= "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s&rsz=8&gl=vn" % text
			text 	= 'https://www.google.com.vn/search?q=intitle:"%s"&sitesearch=xemphim24h.vn&gws_rd=ssl' % text
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
			self.movie_data 	= yield http_client(self.link, c_try=5, c_delay=self.delay)
			data 				= self.movie_data.split('<div class="main_3">', 1)[1]
			data 				= data.split('<!-- end collapsible -->',1)[0]
			
			# poster
			poster 		= "http://xemphim24h.vn" + data.split('src="..',1)[1].split('"',1)[0].strip()
			
			# title
			title 		= data.split('Phim:</td>', 1)[1].split('>',1)[1].split('<',1)[0].strip()
			tmp 		= title.rsplit(' Tập', 1)[0].strip().split(',', 1)
			title 		= tmp[0].strip()
			if len(tmp) > 1:
				subtitle 	= tmp[1].strip()
			else:
				subtitle 	= ""
			
			# director
			try:
				data 		= data.split('Đạo diễn:</td>', 1)
				director 	= [d.strip() for d in data[1].split('">',1)[1].split("<",1)[0].split(',')]
			except:
				traceback.print_exc(file=sys.stdout)
				director 	= ["Đang cập nhật"]
			
			# stars
			data 		= data[1].split('Diễn viên:</td>', 1)
			stars 		= [d.strip() for d in data[1].split('">',1)[1].split("<",1)[0].split(',')]

			# category
			data 		= data[1].split('Thể loại:</td>', 1)
			category 	= [d.strip() for d in data[1].split('">',1)[1].split("<",1)[0].split(',')]

			# country
			country 	= ""
			
			# length
			length 				= {}
			data 				= data[1].split('Tổng số:</td>', 1)
			tmp 				= data[1].split('">',1)[1].split("<",1)[0].strip()
			length['count'] 	= int(tmp.split(' ',1)[0].strip())
			if 'Phút' in tmp:
				length['type'] 	= "short"
			else:
				length['type'] 	= "long"

			# year
			data 		= data[1].split('Sản xuất:</td>', 1)
			year 		= data[1].split('">',1)[1].split("<",1)[0].strip()

			# description
			description 	= data[1].split('<!-- collapsible -->',1)[1].split('<div class="content">',1)[1].split('<!-- end collapsible -->',1)[0].rsplit('</div>',3)[0].strip()
			if '<div class="chudenthuong">' in description:
				description = description.split('<div class="chudenthuong">',1)[1].strip()
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
			servers 	= []
			data 		= self.movie_data.split('<table id="dtloai"',1)[1].split('class="chuxanhdam">', 1)[1].split('<!-- collapsible -->',1)[0]
			srvs 		= data.split('class="chuxanhdam">+ ')
			
			for srv in srvs:
				name 	= srv.split(':</div>',1)[0]
				if '+ ' in name:
					name 	= name.split('+ ',1)[1].strip()
				if 'Picasaweb' in name:
					name 	= "VIP"
				server 	= {
					"name" : name,
					"movie" : []
				}
				chaps 	= srv.split('<div class="chudendam"', 1)[1].rsplit('</a>', 1)[0].split('</a>')
				for chap in chaps:
					name 	= chap.rsplit('">',1)[1].strip()
					link 	= "http://xemphim24h.vn/pages/" + chap.split('<a href="',1)[1].split('"',1)[0]
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
			data 		= yield http_client(link, c_try=5, c_delay=self.delay)
			try:
				data 		= escape.url_unescape(data.split('proxy.link=',1)[1].split('"',1)[0].split('&amp;',1)[0].strip())
			except:
				data 	= data.split('<param name="movie" value="',1)[1].split('"',1)[0]
				data 	= escape.url_unescape(data)
				if 'youtube' in data:
					data = data.split('?',1)[0].strip()
			print(link, data)
			return data
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			return None

