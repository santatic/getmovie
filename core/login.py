import tornado.web
import tornado.auth
from tornado import escape
from core import base

try:
	import urllib.parse as urllib_parse  # py3
except ImportError:
	import urllib as urllib_parse  # py2

class LoginOAuth(base.BaseHandler):
	"""docstring for LoginOAuth"""
	@tornado.gen.coroutine
	def geter(self):
		next 	= self.get_argument('next', None)
		if next:
			self.set_secure_cookie('next', next)
		self.render("login.html")

	# @tornado.gen.coroutine
	# def poster(self):
	# 	# neu email co trong session thi account da login trong database, ko can check lai
	# 	loggedin 	= yield self.loggedin(self.get_argument('email', None))
	# 	if loggedin:
	# 		return self.write("true")

	# 	# neu chua login thi tien hanh login va dang ky neu chua dang ky
	# 	type 	= self.get_argument('type', None)
	# 	if type == "facebook":
	# 		info 	= {
	# 			"id": 			self.get_argument('id', None),
	# 			"email": 		self.get_argument('email', None),
	# 			"access_token": self.get_argument('access_token', None),
	# 			# "first_name": 	self.get_argument('first_name', None)
	# 			# "last_name": 	self.get_argument('last_name', None)
	# 			# "username": 	self.get_argument('username', '')
	# 			# "gender": 		self.get_argument('gender', '')
	# 			# "picture": 		self.get_argument('picture', '')
	# 			# "locale": 		self.get_argument('locale', '')
	# 			# "link": 		self.get_argument('link', '')
	# 			# "quotes": 		self.get_argument('quotes', '')
	# 			# "bio": 			self.get_argument('bio', '')
	# 			# "timezone": 	self.get_argument('timezone', 0)
	# 		}
	# 		if info['id'] and info['email'] and info['access_token']:
	# 			face 	= yield self.facebook_login(info['id'], info['email'], info['access_token'])
	# 			print(face)
	# 			if face:
	# 				print("javascript facebook login successful!")
	# 				return self.write("true")
	# 		print("javascript facebook login failure!")
	# 	else:
	# 		print("login with account!")
	# 		email 		= self.get_argument("email", None)
	# 		password	= self.get_argument("password", None)
	# 		if email and password:
	# 			login 	= yield db_login(email, password)
	# 			if login:
	# 				return self.write("true")
	# 	return self.write("false")

	# @tornado.gen.coroutine
	# def loggedin(self, email):
	# 	session 	= yield self.session.get(['email'])
	# 	if 'email' in session and session['email'] == email:
	# 		return True
	# 	return False
		
	# @tornado.gen.coroutine
	# def set_session(self, info):
	# 	ses 	= {
	# 				"user_id": 			info['user_id'],
	# 				"first_name": 		info['first_name'],
	# 				"last_name": 		info['last_name'],
	# 				"picture": 			info['picture'],
	# 				"email": 			info['email'],
	# 				"type": 			info['type'],
	# 			}
	# 	if 'access_token' in info:
	# 		ses['access_token'] 	= info['access_token']
	# 	self.session.set(ses)
		
	# @tornado.gen.coroutine
	# def db_login(self, email, password):
	# 	db_user = yield self.db.user.find_one(
	# 				{
	# 					'email': 		email,
	# 					'password': 	password
	# 				},{
	# 					'first_name': 1,
	# 					'last_name': 1,
	# 					'picture': 1,
	# 					'email': 1,
	# 				}
	# 			)
	# 	if 'email' in db_user:
	# 		self.set_session({
	# 					"user_id": 			db_user['_id'],
	# 					"first_name": 		db_user['first_name'],
	# 					"last_name": 		db_user['last_name'],
	# 					"picture": 			db_user['picture'],
	# 					"email": 			db_user['email'],
	# 					"type": 			"db",
	# 				})
	# 		return True
	# 	return None

	# @tornado.gen.coroutine
	# def facebook_login(self, id, email, access_token):
	# 	# get information
	# 	face 	= LoginOAuthFacebook(self.application, self.request, **self.kwargs)
	# 	info 	= yield face.facebook_request(
	# 		"/me",
	# 		access_token= access_token,
	# 		# fields="id,email,first_name,last_name,picture,gender,quotes,bio,link,username"
	# 	)
	# 	# if not get info, relogin
	# 	if info and info['email'] == email and info['id'] == id:
	# 		# print(info)
	# 		info['picture'] 		= info['picture']['data']['url']
	# 		# info['locale'] 			= user['locale']
	# 		info['access_token'] 	= access_token
	# 		info['type'] 			= 'facebook'

	# 		# kiem tra user da dang ky trong database chua
	# 		db_user = yield self.db.user.find_one(
	# 					{
	# 						'email': 		email,
	# 						'social.id': 	info['id'],
	# 					},{
	# 						'email': 1
	# 					}
	# 				)
	# 		if not 'email' in db_user:
	# 			# user chua co trong database, no yield for faster
	# 			reg 	= self.registry(info)
	# 			info["user_id"] 	= reg['_id']
	# 			# print("facebook registry: ", info)
	# 		else:
	# 			info["user_id"] 	= db_user['_id']
	# 		# user da co trong database
	# 		# set session logedin, no yield for faster
	# 		self.set_session(info)
	# 		return True
	# 	else:
	# 		return None

	# @tornado.gen.coroutine
	# def registry(self, info):
	# 	###
	# 	insert = yield self.db.user.insert(
	# 		{
	# 			"first_name": 	info['first_name'],
	# 			"last_name": 	info['last_name'],
	# 			"email": 		info['email'],
	# 			"username": 	info['username'],
	# 			"gender": 		info['gender'],
	# 			"picture": 		info['picture'],
	# 			"locale": 		info['locale'],
	# 			"social": 		{
	# 								"id": 			info['id'],
	# 								"type": 		info['type'],
	# 								"link": 		info['link'],
	# 								"quotes": 		info['quotes'],
	# 								"bio": 			info['bio'],
	# 								"access_token": info['access_token'],
	# 								"timezone": 	info['timezone'],
	# 							}
	# 		}
	# 	)
	# 	# print(insert)
	# 	return insert

class LoginOAuthFacebook(base.BaseHandler, tornado.auth.FacebookGraphMixin):
	_OAUTH_ACCESS_TOKEN_URL = "https://graph.facebook.com/v2.1/oauth/access_token?"
	_OAUTH_AUTHORIZE_URL = "https://www.facebook.com/v2.1/dialog/oauth?"
	_FACEBOOK_BASE_URL = "https://graph.facebook.com/v2.1"

	@tornado.gen.coroutine
	def geter(self):
		uri 	= '%s://%s/login/facebook' % (self.request.protocol, self.request.host)
		### next page
		next 	= self.get_argument('next', None)
		if next:
			uri 	= uri + "?next=" + escape.url_escape(next)
		###
		code 	= self.get_argument("code", None)
		if code:
			self.user = yield self.get_authenticated_user(
				redirect_uri	= uri,
				client_id		= self.settings["facebook_oauth"]['key'],
				client_secret	= self.settings["facebook_oauth"]['secret'],
				code			= code
			)
			print('user ---->>>>>>>>>',self.user)
			### authen failure
			if not self.user:
				return self.write("self.user login error!")
			### kiem tra self.user co trong db
			self.info 	= yield self.db.user.find_one(
						{
							'social.id': self.user['id']
						},{
							'first_name': 1,
							'last_name': 1,
							'picture': 1,
							'email': 1,
						}
					)
			### self.user don't exist
			if not self.info:
				# get self.information
				self.info = yield self.facebook_request(
					"/me",
					access_token= self.user["access_token"],
					fields="picture.type(large),bio,birthday,email,gender,first_name,last_name,name,link,timezone",
				)
				### login update
				if self.info:
					print('me ---->>>>>>>>>',self.info)
					self.info['picture'] 		= self.user['picture']['data']['url']
					self.info['locale'] 		= self.user['locale']
					self.info['access_token'] 	= self.user["access_token"]
					### add database , add after redirect for faster
					# print(self.info)
					self.info['_id'] 			= yield self.registry(self.info)
				else:
					return self.write("self.user login error!")
			### set session
			ses 	= {
				"access_token": 	self.user['access_token'],
				"user_id": 			self.info['_id'],
				"first_name": 		self.info['first_name'],
				"last_name": 		self.info['last_name'],
				"picture": 			self.info['picture'],
				"type": 			"facebook",
			}
			if 'email' in self.info:
				ses['email'] 	= self.info['email']
			yield self.session.set(ses)

			### background job
			yield self.backgroud_obj()
			### redirect to next page
			self.redirect(self.get_argument('next', '/'))
		else:
			# yield self.login()
			yield self.authorize_redirect(
				redirect_uri	= uri,
				client_id		= self.settings["facebook_oauth"]['key'],
				# extra_params	= {"scope": "email,publish_actions,read_friendlists,user_about_me,user_birthday,user_friends,user_location,manage_friendlists"}
				extra_params	= {"scope": "email,user_about_me,user_friends,user_birthday,user_likes,user_status"}
			)

	@tornado.gen.coroutine
	def registry(self, info):
		query 	= {
				"first_name": 	info['first_name'],
				"last_name": 	info['last_name'],
				"gender": 		info['gender'],
				"picture": 		info['picture'],
				"locale": 		info['locale'],
				"birthday": 	info['birthday'],
				"social": 		{
									"id": 			info['id'],
									"type": 		"facebook",
									"link": 		info['link'],
									# "quotes": 		info['quotes'],
									# "bio": 			info['bio'],
									"access_token": info["access_token"],
									"timezone": 	info["timezone"],
								}
			}
		if 'email' in info:
			query["email"] 		= info['email']

		if "username" in info:
			query["username"] 	= info['username']
		insert = yield self.db.user.insert(query)
		return insert


	@tornado.gen.coroutine
	def backgroud_obj(self):
		yield self.get_friends()

	@tornado.gen.coroutine
	def get_friends(self):
		result = yield self.facebook_request(
			"/me",
			access_token = self.user["access_token"],
			fields = 'context.fields(mutual_friends.limit(5000))'
		)
		print('friends', result)

		if 'context' in result and 'mutual_friends' in result['context']:
			result = result['context']['mutual_friends']

		while 'paging' in result and 'cursors' in result['paging'] and 'after' in result['paging']['cursors']:
			result = yield self.facebook_request(
				"/me",
				access_token = self.user["access_token"],
				fields = 'context.fields(mutual_friends.limit(5000).after(%s))' % result['paging']['cursors']['after']
			)
			# param = result['paging']['next'].split('?',1)[1].split('&')
			# data = {}
			# for p in param:
			# 	p = p.split('=')
			# 	data[p[0]] = p[1]
			# result = yield self.facebook_request(
			# 	"/me/friends",
			# 	**data
			# )
			print('friends', result)
			if 'context' in result and 'mutual_friends' in result['context']:
				result = result['context']['mutual_friends']




# https://graph.facebook.com/v2.1/100001734918068?fields=context.fields(mutual_friends.limit(500).after(NTYzODc0OTIwMzkyMDQ0))







# class LoginOAuthGoogle(base.BaseHandler, tornado.auth.GoogleOAuth2Mixin):
# 	"""docstring for LoginOAuthGoogle"""
# 	# @tornado.web.asynchronous
# 	@tornado.gen.coroutine
# 	def geter(self):
# 		if self.get_argument('code', False):
# 			user = yield self.get_authenticated_user(
# 				redirect_uri='http://localhost:8888/login/google',
# 				code=self.get_argument('code')
# 			)
# 			# print(user)
# 			info = yield self._user_info(user)
# 			# print(info)
# 			plus = yield self._user_plus(user)
# 			# print(plus)
# 			# friends = yield self._user_friends(user)
# 			# print(friends)

# 			self.settings["db"].users.insert({
# 				'given_name':	info['given_name'],
# 				'family_name': 	info['family_name'],
# 				'email': 		info['email'],
# 				'full_name': 	info['name'],
# 				'picture': 		info['picture'],
# 				'gender': 		info['gender'],
# 				'locale': 		info['locale'],
# 			}, callback=self.on_inserted)

# 			# set session
# 			yield self.session.set("email", info['email'])
# 			# result
# 			self.write("done!")
# 			self.redirect("/page")
# 		else:
# 			yield self.authorize_redirect(
# 				redirect_uri	= 'http://localhost:8888/login/google',
# 				client_id		= self.settings[self._OAUTH_SETTINGS_KEY]['key'],
# 				scope			= [
# 									'https://www.googleapis.com/auth/userinfo.profile',
# 									'https://www.googleapis.com/auth/userinfo.email',
# 									'https://www.googleapis.com/auth/plus.login',
# 									'https://www.googleapis.com/auth/plus.me',
# 									# 'https://www.googleapis.com/auth/plus.circles.read',
# 									# 'https://www.googleapis.com/auth/plus.circles.write',
# 									# 'https://www.googleapis.com/auth/plus.stream.read',
# 									# 'https://www.googleapis.com/auth/plus.stream.write',
# 									# 'https://www.googleapis.com/auth/plus.media.upload',
# 									'https://www.google.com/m8/feeds',
# 								],
# 				response_type	= 'code',
# 				extra_params	= {'approval_prompt': 'auto'})

# 	def _oauth_get_info(self, user, uri, callback):
# 		http = self.get_auth_http_client()
# 		http.fetch(
# 			uri,
# 			self.async_callback(self._on_access_token, callback),
# 			method="GET",
# 			headers={
# 				'Content-Type': 'application/x-www-form-urlencoded',
# 				'Authorization': 'Bearer ' + str(user['access_token'])
# 			}
# 		)

# 	@tornado.auth._auth_return_future
# 	def _user_info(self, user, callback):
# 		self._oauth_get_info(user, "https://www.googleapis.com/oauth2/v1/userinfo?=%s" % (user['access_token']), callback)


# 	@tornado.auth._auth_return_future
# 	def _user_plus(self, user, callback):
# 		self._oauth_get_info(user, "https://www.googleapis.com/plus/v1/people/me?access_token=%s" % (user['access_token']), callback)

# 	# @tornado.auth._auth_return_future
# 	# def _user_friends(self, user, callback):
# 	# 	self._oauth_get_info(user, "https://www.googleapis.com/plus/v1/people/list?access_token=%s" % (user['access_token']), callback)


# 	def on_inserted(self, result, error):
# 		self.settings["db"].users.find().to_list(callback=self.got_users)

# 	def got_users(self, users, error):
# 		if error:
# 			print('error getting users!', error)
# 		else:
# 			for user in users:
# 				print(user)
