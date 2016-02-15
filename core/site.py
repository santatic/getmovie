import os, re, logging
import tornado.web
import tornado.gen
import tornado.websocket
from bson.objectid import ObjectId
from tornado import escape
from base64 import b64encode
from urllib.parse import urlparse
from core import base, function
from core.app import movie

import sys, traceback

class Site(base.BaseHandler):
	"""docstring for Site"""
	@tornado.gen.coroutine
	def geter(self, site_page=None):
		if site_page == "search":
			return {"action": "result", "data": self.render_string("searcher.html").decode('utf-8')}
		return {"action": "result", "data": self.render_string("geter.html").decode('utf-8')}

	@tornado.gen.coroutine
	def poster(self, site_page, site_post=None, site_seo=None):
		pass

class SiteWS(tornado.websocket.WebSocketHandler, Site):
	"""docstring for SiteWS"""
	def __init__(self, application, request, **kwargs):
		Site.__init__(self, application, request, **kwargs)
		tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
	# pass webhandler
	def finish(self):
		pass

	def open(self):
		self._ws_inited 		= False
		self._module_inited 	= None

	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def on_message(self, message):
		print('msg : ',message)
		try:
			if not self._ws_inited:
				self._ws_inited 	= True
				self.generic 		= movie.MovieGeneric(self)
				print('[+] inited')
				return self.write_message('{"ok":1}')
			else:
				yield self.ws_read(message)
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	@tornado.gen.coroutine
	def ws_read(self, msg):
		msg 	= escape.json_decode(msg)
		if not self._module_inited:
			if 'action' in msg:
				if msg['action'] == 'generic':
					self._module_percent 	= 0
					self._module_inited 	= True
					self.ws_info 			= {
						"action" 	: msg['action'],
						"link"		: msg['link']
					}
					self._module_percent 	+= 5
					self.write_message('{"ok":1,"data":{"percent":%s,"log": "[+] Get link %s inited !"}}' % (self._module_percent, msg['link']))
					self.generic_site()
				elif msg['action'] == 'search':
					self.ws_info 			= {
						"action" 		: msg['action'],
						"search"		: msg['search']
					}
					self.search_site()
					self._module_inited 	= True

	@tornado.gen.coroutine
	def ws_flush(self, data, ws_is="process"):
		self.write_message('{"ok":1,"is":"%s","data":%s}' % (ws_is, escape.json_encode(data)))
	
	@tornado.gen.coroutine
	def search_site(self):
		try:
			result 	= yield self.generic.search_movie(self.ws_info['search'])
			yield self.ws_flush({"percent": 100,"log":"Generic finished!","data": result}, ws_is="finish")
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	@tornado.gen.coroutine
	def generic_site(self):
		try:
			# get information
			result 	= yield self.generic.get_info(self.ws_info['link'])
			print('info',result)
			self._module_percent 	+= 5
			self.ws_flush({"percent": self._module_percent, "log": "[+] getted movie info %s"% escape.json_encode(result)})
			
			# get movie and standard movie
			result 	= yield self.generic.get_movie(self.ws_info['link'])
			print('servers',result)
			self._module_percent 	+= 5
			self.ws_flush({"percent": self._module_percent, "log": "[+] getted movie servers %s"% escape.json_encode(result)})

			# decrypt & update cache
			result 	= yield self.generic.get_parts(callback_info=self._generic_part_info)
			print('parts',result)

			# complete 
			self.ws_flush({"percent": 100,"log":"Generic finished!","data": self.generic.get_store()}, ws_is="finish")
		except Exception as e:
			traceback.print_exc(file=sys.stdout)

	# private function callback info decrypt & update cache
	def _generic_part_info(self, log):
		self._module_percent 	+= 1
		self.ws_flush({"percent": self._module_percent, "log": log})

	def close(self):
		if self.generic:
			self.generic.close()
			del self.generic

	def on_close(self):
		pass
