import motor
# import pickle
import hashlib

from time import mktime
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from tornado import gen
from uuid import uuid1


class Session(object):
	"""
	table: session,
		@session_id : id cua session, duoc set trong cookie
		@expired_time: thoi gian het han session
		@user_id : _id trong table user
	"""
	def __init__(self, db, session_id=None):
		self.db 			= db
		self.session_id 	= session_id
		self.life_length 	= timedelta(days=7)
		self.store 			= None

	@gen.coroutine
	def isalive(self):
		# assert self.session_id
		session = None
		if self.session_id != None:
			session = yield self.db.find_one({
				'session_id': self.session_id
			})
		if session:
			if session['expired_time'] < int(mktime(datetime.now().timetuple())):
				# delete session
				yield self.db.remove({
					'session_id': self.session_id
				})
				session = None
			else:
				session = session["session_id"]
		else:
			session = yield self.generate_session_id()
			self.session_id = session
			res = yield self.new_session()
		# print("isalive with session:", session)
		return session

	@gen.coroutine
	def set(self, query):
		assert self.session_id
		result 		= yield self.db.update({
							'session_id': self.session_id
						},{
							'$set': query
						}
					)
		self.store 	= None
		return result

	@gen.coroutine
	def get(self, query):
		assert self.session_id
		if not self.store:
			self.store 	= yield self.db.find_one({
				'session_id': self.session_id
			})
		return self.store

	@gen.coroutine
	def delete(self, key):
		'''Delete a key'''
		assert self.session_id
		result = yield self.db.update({
			'session_id': self.session_id,
			'$unset': {key: ''}
		})
		return result

	@gen.coroutine
	def new_session(self):
		'''New session on server'''
		assert self.session_id
		result = yield self.db.insert({
			'session_id': self.session_id,
			'expired_time': int(mktime((datetime.now() + self.life_length).timetuple())) # 3 days
		})
		return result

	@gen.coroutine
	def refresh_session(self):
		'''Refresh session every other `regeneration_interval`'''
		assert self.session_id

		refresh_session_id = None
		expired_time = yield self.get('expired_time')

		now = int(mktime(datetime.now().timetuple()))
		if now > expired_time:
			refresh_session_id = yield self.generate_session_id()
			result = yield self.db.update({
				'session_id': self.session_id, 
				'$set': {
					'session_id': refresh_session_id,
					'expired_time': int(mktime((datetime.now() + self.life_length).timetuple()))
				}
			})
		self.session_id = refresh_session_id
		return refresh_session_id

	@gen.coroutine
	def clear_old(self):
		'''Delete a key'''
		assert self.session_id
		result = yield self.db.remove({
			'expired_time': {'$lt': int(mktime(datetime.now().timetuple()))}
		})
		return result

	@gen.coroutine
	def life(self, sid):
		# assert self.session_id
		session = yield self.db.find_one({
			'session_id': sid,
			'expired_time': {
				'$gt': int(mktime(datetime.now().timetuple()))
			}
		})
		return session

	@gen.coroutine
	def generate_session_id(self):
		'''Generate a session id'''
		sid = None
		while True:
			# print("generate_session_id looping!")
			m = hashlib.md5()
			m.update((str(uuid1()) + str(datetime.now())).encode("utf-8"))
			sid = m.hexdigest()
			session = yield self.life(sid)
			if session == None:
				break
		return sid