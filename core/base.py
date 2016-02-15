import sys, traceback
import urllib.parse
import functools
import motorsession

from tornado import web, gen, escape

class BaseHandler(web.RequestHandler):
	def __init__(self, application, request, **kwargs):
		super(BaseHandler, self).__init__(application, request, **kwargs)
		self.application 	= application
		self.request 		= request
		

	@gen.coroutine
	def initer(self):
		pass

	@gen.coroutine
	def geter(self):
		return None

	@gen.coroutine
	def poster(self):
		return None

	@web.asynchronous
	@gen.coroutine
	def get(self, *args, **kwargs):
		try:
			yield self.initer()
			result 	= yield self.geter(*args, **kwargs)
			if result and 'action' in result:
				if result['action'] == "redirect":
					return self.redirect(result['data'])
				elif result['action'] == "result":
					if type(result['data']) in [dict, list]:
						return self.write(escape.json_encode(result['data']))
					return self.write(result['data'])
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		if not self._finished:
			return self.write('')
			self.finish()

	@web.asynchronous
	@gen.coroutine
	def post(self, *args, **kwargs):
		try:
			yield self.initer()
			result 	= yield self.poster(*args, **kwargs)
			if result and 'action' in result:
				if result['action'] == "redirect":
					return self.redirect(result['data'])
				elif result['action'] == "result":
					if type(result['data']) in [dict, list]:
						return self.write(escape.json_encode(result['data']))
					return self.write(result['data'])
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		if not self._finished:
			return self.write('')
			self.finish()