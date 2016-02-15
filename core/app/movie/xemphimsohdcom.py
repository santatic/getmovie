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

		self.data = ""

	@gen.coroutine
	def search(self, text):
		movies 	= []
		try:
			text 	= escape.url_escape(text)
			# text 	= "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s&rsz=8&gl=vn" % text
			text 	= 'https://www.google.com.vn/search?q=intitle:"%s"&sitesearch=xem.phimsohd.com&gws_rd=ssl' % text
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
			self.data 	= yield http_client(self.link, c_try=5, c_delay=self.delay)
			data 		= self.data.split(" id='thongtinphim'>", 1)[1]
			data 		= data.split('<div class="description">',1)[0]
			
			# trailer
			try:
				trailer 	=["https://www.youtube.com/watch?v="+data.split('Trailer;phimsohd.y/',1)[1].split('|',1)[0].strip()]
			except:
				trailer 	= ""

			# poster
			poster 		= data.split('<img src="',1)[1].split('"',1)[0].strip()
			
			
			# title
			title 		= data.split('<b class="thongtin tenphim">Phim: </b>', 1)[1].split('</h2>',1)[0].strip()
			tmp 		= title.split(' - ', 1)
			title 		= tmp[0].strip()
			if len(tmp) > 1:
				subtitle 	= tmp[1].strip()
			else:
				subtitle 	= ""
			

			# length
			length 	= {}
			try:
				tmp 				= data.split('<b class="thongtin">Tập: </b>', 1)[1].split("<br />",1)[0].strip()
				length['count'] 	= int(tmp.split(' ',1)[0].strip())
				if 'Tập' in tmp:
					length['type'] 	= "long"
			except:
				length['count']		= 100
				length['type'] 		= "short"
			


			# category
			category 	= [d.strip() for d in data.split('<b class="thongtin">Thể loại: </b>', 1)[1].split('<br />',1)[0].split(',')]

			# director
			director 	= []
			
			# stars
			stars 		=  [d.strip() for d in data.split('<b class="thongtin">Thể loại: </b>', 1)[1].split('<br />',1)[0].split(',')]

			
			# year
			year 		= data.split('<b class="thongtin">Năm PH: </b>',1)[1].split('<br />',1)[0].strip()
			
			
			# country
			country 	= data.split('<b class="thongtin">Quốc gia: </b>',1)[1].split('<br />',1)[0].strip()

			# description
			description 	= data.split('<b class="thongtin">Giới thiệu: </b>',1)[1].split('</div>',1)[0].strip()
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
			
			servers 	= []
			data 		= self.data.split('class="tapphim">\n<id>',1)[1].split('|</id>',1)[0]
			data 		= data.split('|')
			videos 		= []
			for v in data:
				if v:
					v = v.split(';')
					if len(v) > 1 and v[1].strip():
						video = []
						if len(v) == 2:
							videos.append({
								"name": v[0]+ "-Full",
								"source": [v[1]]
								})
						else:
							for i, vi in enumerate(v[1:], start=1):
								videos.append({
									"name": "%s-%s" % (v[0], i),
									"source": [v[i]]
								})
			movies = {}
			for v in videos:
				if "phimsohd.y/" in v['source'][0]:
					v['source'][0] = "https://www.youtube.com/watch?v=" + v['source'][0].split('phimsohd.y/', 1)[1].strip()
				elif "phimsohd.com/" in v['source'][0]:
					v['source'][0] = "http://" + v['source'][0].split('phimsohd.com/', 1)[1].strip()

					
				if 'picasaweb' in v['source'][0]:
					name = "VIP"
				elif 'youtube' in v['source'][0]:
					name = "VIP 2"
				else:
					print(v['source'][0])
					name = v['source'][0].split('.',1)[0].rsplit('/',1)[1]

				if not name in movies:
					movies[name] = []
				movies[name].append(v)

			servers = []
			for v in movies:
				servers.append({
						"name" : v,
						"movie" : movies[v]
					})
			return servers
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		
	@gen.coroutine
	def get_link(self, link):
		return link

