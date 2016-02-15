from .. import AppManager
from . import phim14net, phimvangorg, phimhdvn, xemphim24hvn, movievndailyscom, phimhay365com, phimtructuyenhdcom, xemphim2com, xemphimsohdcom, phimtvvn
from core import function

from tornado import gen, escape
from bson.objectid import ObjectId
from bson.code import Code
from time import time

import re

import sys, traceback

############# MOVIE GENERIC ##############
class MovieGeneric(object):
	"""docstring for MovieGeneric"""
	def __init__(self, site):
		self.site 		= site
		self.movie 		= []
	
	# ham dung de detech "source site"
	def _get_movie_obj(self, link=None, all=False):

		if all or 'phimtv.vn' in link:
			self.movie.append(phimtvvn.MovieGeneric(link))
		if all or 'xem.phimsohd.com' in link:
			self.movie.append(xemphimsohdcom.MovieGeneric(link))
		if all or 'xemphim2.com' in link:
			self.movie.append(xemphim2com.MovieGeneric(link))
		if all or 'phimtructuyenhd.com' in link:
			self.movie.append(phimtructuyenhdcom.MovieGeneric(link))
		if all or 'phimhay365.com' in link[:30]:
			self.movie.append(phimhay365com.MovieGeneric(link))
		if all or 'movie.vndailys.com' in link[:30]:
			self.movie.append(movievndailyscom.MovieGeneric(link))
		if all or 'xemphim24h.vn' in link[:25]:
			self.movie.append(xemphim24hvn.MovieGeneric(link))
		if all or 'phimhd.vn' in link[:20]:
			self.movie.append(phimhdvn.MovieGeneric(link))
		if all or 'phimvang.org' in link[:21]:
			self.movie.append(phimvangorg.MovieGeneric(link))
		# if all or 'phim14.net' in link[:18]:
		# 	self.movie.append(phim14net.MovieGeneric(link))
		
		
		
		
		
		
		
		
		if not all:
			self.movie = self.movie[0]

		self.movie_info 	= {"source": [link]}
		return True
	
	@gen.coroutine
	def search_movie(self, search):
		try:
			print('search movie', search)
			if not self.movie:
				self._get_movie_obj(all=True)
			futures = []
			for m in self.movie:
				result = m.search(search)
				futures.append(result)
			result = yield gen.multi_future(futures)
			return result
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	def get_store(self):
		try:
			return self.movie_info
		except Exception as e:
			return {}

	# generic movie information
	# ham dung de lay info cua 1 bo phim
	# ten/nam san suat/dien vien/ gioi thieu ...
	@gen.coroutine
	def get_info(self, link):
		try:
			if not self.movie:
				self._get_movie_obj(link)

			result 	= yield self.movie.get_info()
			self.movie_info.update(result)
			return result
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	# generic movie chaps
	# ham dung de decrypt (neu co) va get link cua moi part tren "source site"
	@gen.coroutine
	def get_movie(self, link):
		try:
			if not self.movie:
				self._get_movie_obj(link)

			result 	= yield self.movie.get_servers()
			self.movie_info['server'] 	= result

			# standard movie
			result 	= self.movie_standard()
			self.movie_info['movie'] 	= result
			del self.movie_info['server']

			return result
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	# sort movie of list server generic to standard
	# khi generic movie chi lay dc list servers[parts]
	# can phai chuan hoa ve dang chaps/servers/parts
	def movie_standard(self, servers=None, mv_type=None):
		try:
			if not servers and 'server' in self.movie_info:
				servers 	= self.movie_info['server']

			if not mv_type:
				if 'length' in self.movie_info and type(self.movie_info['length']) == dict:
					mv_type 	= self.movie_info['length']['type']
				else:
					mv_type 	= "long"

			if servers:
				try:
					movie 	= {}
					for server in servers:
						for part in server['movie']:
							if mv_type == "short":
								name 	= "Xem Phim"
							else:
								name 		= part['name']
								try:
									name 	= int(re.search(r"^(\d+)", name).groups(0)[0])
								except Exception as e:
									pass
							imported 	= False
							if not name in movie:
								movie[name] 	= []

							# neu server da co trong movie[part] thi append vao movie
							for srv in movie[name]:
								if srv['name'] == server['name']:
									srv['part'].append(part)
									imported 	= True
									break
							# neu server chua co trong chaps thi them server vao movie[chap]
							if not imported:
								movie[name].append({
									"part": [part],
									"name": server['name']
								})
					result 	= []
					for chap_name in movie:
						result.append({"name": str(chap_name), "server": movie[chap_name]})
					return result
				except Exception as e:
					traceback.print_exc(file=sys.stdout)
			return None
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	# generic (decrypt/cache) all movie server part
	@gen.coroutine
	def get_parts(self, movies=None, callback_info=None):
		try:
			if not movies and 'movie' in self.movie_info:
				movies 	= self.movie_info['movie']
			if movies:
				result 	= []
				for chap in movies:
					# chap 			= movies[chap]
					result_chap 	= {'name': chap['name'],'server':[]}
					for server in chap['server']:
						# server 			= chap['server'][server]
						result_server 	= {'name': server['name'],'part':[]}
						for part in server['part']:
							# part 	= server['part'][part]

							if not 'link' in part and 'source' in part and len(part['source']) > 0:
								# decrypt & get link movie
								g_movie, g_link 	= yield self.part_decrypt(part['source'][-1])
								if callback_info:
									callback_info('geted part: %s' % part['source'][0])
								if g_movie:
									if not g_movie in part['source']:
										part['source'].append(g_movie)
									if g_link:
										part['link'] 	= g_link
										# update cache
										cache 	= yield self.part_cache(g_link)
										if cache:
											if callback_info:
												callback_info('geted cache: %s' % g_link)
											part['cache']	= cache
							result_server['part'].append(part)
						server.update(result_server)
						result_chap['server'].append(server)

					chap.update(result_chap)
					result.append(chap)
				return result
			return None
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	@gen.coroutine
	def part_decrypt(self, link):
		try:
			if not self.movie:
				self._get_movie_obj(link)

			# get and decrypt movie link
			g_movie 	= yield self.movie.get_link(link)
			if g_movie:
				g_link 	= yield self.part_link(g_movie)
			else:
				g_link 	= None
			return g_movie, g_link
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	@gen.coroutine
	def part_link(self, g_movie, link=None):
		try:
			if '.google.com' in g_movie[:28]:
				u_id 		= ""
				p_id 		= ""
				u_auth 		= ""

				if 'picasaweb' in g_movie[:18]:
					if '#' in g_movie:
						regex 	= re.compile("https://picasaweb.google.com/([a-z0-9]+)/(.*?)authkey=([a-zA-Z0-9\-\_\+]+)(.*?)#([a-z0-9]+)")
						r 		= regex.search(g_movie)
						if r:
							lst 	= r.groups()
							u_id 	= lst[0]
							u_auth	= lst[2]
							p_id 	= lst[4]
						else:
							print('\n\n\n\n mvi',g_movie)
							regex 	= re.compile("https://picasaweb.google.com/([a-z0-9]+)/(.*?)#([a-z0-9]+)")
							# https://picasaweb.google.com/106316564981908873085/Vsub?noredirect=1#6060808208011471442
							r 		= regex.search(g_movie)
							lst 	= r.groups()
							u_id 	= lst[0]
							p_id 	= lst[2]
					
					elif "/lh/photo/" in g_movie:
						data 	= yield function.http_client(g_movie, c_try=5, c_delay=3)
						# regex 	= re.compile(r"\:\\x2F\\x2Fplus\.google\.com\\x2Fphotos\\x2F([a-zA-Z0-9]+)\\x2Fphoto\\x2F([a-zA-Z0-9]+)\?")
						regex 	= re.compile(r"picasaweb.google.com/data/feed/tiny/user/([0-9]+)/photoid/([0-9]+)\?(.*?)\"")
						r 		= regex.search(data)
						lst 	= r.groups()
						return "https://picasaweb.google.com/data/feed/tiny/user/%s/photoid/%s?%s" % (lst[0],lst[1],lst[2])
					else:
						data 	= yield function.http_client(g_movie, c_try=5, c_delay=3)

						regex 	= re.compile("\"(https://picasaweb.google.com/data/feed/tiny/user/([a-z0-9]+)/albumid/([a-z0-9]+)/photoid/([a-z0-9]+)(.*?))\"")
						r 		= regex.search(data)
						lst 	= r.groups()

						mv 		= lst[0]
						u_id 	= mv.split('tiny/user/', 1)[1].split('/',1)[0]
						p_id 	= mv.split('photoid/', 1)[1].split('/',1)[0].split('?',1)[0]
						try:
							u_auth 	= mv.split('authkey=', 1)[1].split('/',1)[0].split('?',1)[0].split('&',1)[0]
						except Exception as e:
							print('authen key error', self, e)

					g_link 	= "https://picasaweb.google.com/data/feed/tiny/user/%s/photoid/%s?alt=jsonm" % (u_id, p_id)
					if len(u_auth) > 0:
						g_link 		= "%s&authkey=%s" % (g_link, u_auth)
					
					return g_link
				elif 'docs' in g_movie[:12]:
					return g_movie
				
			elif 'youtube.com' in g_movie[:28] or 'youtu.be' in g_movie[:15]:
				return g_movie
			elif 'clip.vn' in g_movie[:28]:
				return g_movie
			elif 'tv.zing.vn' in g_movie[:28]:
				return g_movie
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			return None

	@gen.coroutine
	def part_cache(self, link):
		try:
			cache 	= {'expire': 0}
			if 'picasaweb' in link[:18]:
				data 			= yield function.http_client(link, c_try=5, c_delay=0)
				if data:
					data 			= escape.json_decode(data)
					cache['video'] 	= []
					video 			= data['feed']['media']['content']
					for v in video:
						if not cache['expire'] and 'expire' in v['url']:
							cache['expire'] 	= int(v['url'].split('expire=',1)[1].split('&',1)[0])

						if 'type' in v and (v['type'].startswith('video/') or v['type'].startswith('application/')):
							cache['video'].append(v)
					return cache
			# elif 'youtube.com' in link[:28] or 'youtu.be' in link[:16]:
			# 	cache['expire'] 	= 9999999999
			# 	# http://youtu.be/x2J6YQS8RRE
			# 	if 'youtu.be/' in link[:17]:
			# 		vd_id 	= link.split('youtu.be/',2)
			# 		if len(vd_id) > 1:
			# 			cache['video'] 	= "https://www.youtube.com/watch?v=%s" % vd_id[1]

			# 	if not 'video' in cache:
			# 		cache['video'] 		= link
			# 	return cache

			return None
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	def close(self):
		pass