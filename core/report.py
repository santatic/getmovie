from tornado import gen

class SiteReport(object):
	"""docstring for SiteReport"""
	def __init__(self, site):
		self.site 		= site
		self.site_id 	= None
		self.user_id 	= None

	@gen.coroutine
	def user_init(self):
		if not self.site_id:
			self.site_id 	= self.site.site_db['_id']
		
		if not self.user_id:
			session 	= yield self.site.session.get(['user_id'])
			if 'user_id' in session:
				self.user_id 	= session['user_id']

		if self.site_id and self.user_id:
			return True
		return False

	@gen.coroutine
	def set(self, type, content):
		if type in ['update_chap', 'film_die', 'film_slow', 'others'] and (yield self.user_init()):
			result = yield self.site.db.site_report.insert({
				"site_id": self.site_id,
				"format": "rpmv",
				"data": {
					"user": self.user_id,
					"type": type,
					"content": content
				}
			})
			return result
		return None