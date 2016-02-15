# import tornado.web
# import tornado.auth

import re
import motor
from tornado import web, escape, gen

from core import base

class Register(base.BaseHandler):
	"""docstring for Register"""
	@gen.coroutine
	def geter(self):
		self.render("register.html", error=None)

	@gen.coroutine
	def poster(self):
		email 			= self.get_argument('email', None)
		given_name 		= self.get_argument('given_name', None)
		family_name 	= self.get_argument('family_name', None)
		password 		= self.get_argument('password', None)
		repassword		= self.get_argument('repassword', None)

		error 			= None
		if re.match(r'(\w+[.|\w])*@(\w+[.])*\w+', email):
			print("email success!")
			if re.match(r'^[\w|.|-|_| ]+$', given_name, re.UNICODE):
				print("given_name success!")
				if re.match(r'^[\w|.|-|_| ]+$', family_name, re.UNICODE):
					print("family_name success!")
					if len(password) > 5 and password == repassword:
						print("password success!")
					else:
						error = "password failure!"
				else:
					error = "family_name failure!"
			else:
				error = "given_name failure!"
		else:
			error = "email failure!"

		if not error:
			result = yield motor.Op(self.db.users.find_one, {'email': email})
			print("db result: ", result)
			if result:
				error = "email exist!"
			else:
				result = yield motor.Op(self.db.users.insert, {
							'email': 		email,
							'given_name': 	given_name,
							'family_name': 	family_name,
							'password': 	password,	
						})
				print(result)

		if error:
			print(error)
			self.render("register.html", error=error)
		else:
			self.write("Done!")