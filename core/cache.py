from tornado import gen
from bson.binary import Binary
import pickle, hashlib, time

class CacheManager(object):
	"""docstring for CacheManager"""
	def __init__(self, db):
		self.db 	= db
	
	@gen.coroutine
	def set(self, source, data, expire):
		# build key md5
		m 		= hashlib.md5()
		m.update(source.encode("utf-8"))
		md5 	= m.hexdigest()

		# insert cache
		result 	= yield self.db.insert({
			"key": md5,
			"expire": int(time.time()) + expire,
			"source": source,
			"data": Binary(pickle.dumps(data))
		})
		return md5, result

	@gen.coroutine
	def get(self, key=None, source=None):
		if not key and source:
			m 		= hashlib.md5()
			m.update(source.encode("utf-8"))
			key 	= m.hexdigest()

		if key and len(key) == 32:
			query = {"key": key}
			# now
			query['expire'] = {"$gte": int(time.time())}

			result 	= yield self.db.find_one(query,{'data':1})

			if result and "data" in result:
				return pickle.loads(result['data'])
		return None

	@gen.coroutine
	def clear(self):
		result = yield self.db.remove({"expire": {"$lt":int(time.time())}})
		return result