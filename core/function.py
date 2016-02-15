import os, re, time, hashlib
from tornado import ioloop, gen, httpclient

import sys, traceback

###
char_map 	= { 'a' : "áàảạãâấầẩậẫăắằẳặẵ",
				'e' : "éèẻẹẽêếềểệễ",
				'i' : "íìỉịĩ",
				'o' : "óòỏọõôốồổộỗơớờởợỡ",
				'u' : "úùủụũưứừửựữ",
				'y' : "ýỳỷỵỹ",
				'd' : "đ",
			}
def seo_encode(string):
	string 		= string[0:50].strip().lower()
	for key, val in char_map.items():
		for char in val:
			string = string.replace(char, key)

	string 	= string.encode('ascii', 'ignore').decode('ascii')
	string 	= re.sub('[^\w\s-]', '', string)
	return re.sub('[-\s]+', '-', string)

###
mobile_useragent 		= ['android','sony','symbian','nokia','samsung','mobile','windows ce','epoc','opera mini','nitro','j2me','midp-','cldc-','netfront','mot','up.browser','up.link','audiovox','blackberry','ericsson,','panasonic','philips','sanyo','sharp','sie-','portalmmm','blazer','avantgo','danger','palm','series60','palmsource','pocketpc','smartphone','rover','ipaq','au-mic,','alcatel','ericy','up.link','docomo','vodafone/','wap1.','wap2.','plucker','480x640','sec','fennec','google wireless transcoder','nintendo','webtv','playstation']
def mobile_detect(useragent):
	if useragent:
		useragent 	= useragent.lower()
		for s in mobile_useragent:
			if s in useragent:
				return "mobile"
	return "desktop"

###
httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
@gen.coroutine
def http_client(link, c_headers=None, c_try=3, c_delay=3):
	try:
		cache_dir 	= 'cache/http_client'
		m 	= hashlib.md5()
		m.update(link.encode("utf-8"))
		link_md5 	= m.hexdigest()
		links_md5 	= os.listdir(cache_dir)
		now 	= int(time.time())
		for l in links_md5:
			if os.path.isfile(cache_dir + '/' +l) and re.match(r''+link_md5+r'\.([0-9]+)', l):
				print('cache link', l)
				if int(l.rsplit('.',1)[1]) > now - 864000:
					with open(cache_dir + '/' +l, encoding='utf-8', mode='r') as f:
						data = f.read()
					f.close()
					return data
				else:
					os.remove(cache_dir + '/' +l)
		###
		headers 	= {
			"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:30.0) Gecko/20100101 Firefox/30.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5"
		}
		if c_headers:
			headers.update(c_headers)

		try_current 	= 0
		data 			= ""
		while try_current < c_try:
			# time.sleep(c_delay)
			yield gen.Task(ioloop.IOLoop.instance().add_timeout, time.time() + c_delay)
			print('[%s] get link: %s' % (try_current, link))
			http_client 	= httpclient.AsyncHTTPClient()
			try:
				response 	= yield http_client.fetch(link, method="GET", headers=headers, connect_timeout=30.0, request_timeout=30.0, validate_cert=False)
				data 		= response.body.decode('utf-8')
				break
			except Exception as e:
				print('http_client error', e)
				try_current 		+= 1
			http_client.close()

		f = open(cache_dir +'/'+link_md5+"."+str(now) , encoding='utf-8', mode='w+')
		f.write(data)
		f.close()
		return data
	except Exception as e:
		traceback.print_exc(file=sys.stdout)
	