#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, logging
# pass library load
sys.path.append(os.path.abspath('library'))
import motor

from tornado import web, options, ioloop, httpserver
from tornado.options import define, options
from core import site
###################
define("port", default=8888, help="run on the given port", type=int)
###################
class Application(web.Application):
	def __init__(self):
		handlers = [
			(r"/ws", site.SiteWS),
			(r"/?(.*?)", site.Site),
		]
		settings = {
			'debug'					: True,
			'cookie_secret'			: "iTfgAulVRmq2KO9CFYdPwla+45Mzs0s9g5Vtt5wNtQA1V5qnvO5L+qmWGmpyGsGw1",
			'template_path'			: os.path.join(os.path.dirname(__file__), "template"),
			'static_path'			: os.path.join(os.path.dirname(__file__), "static"),
			'login_url'				: "/login",
			'xheaders' 				: True,
		}
		# clear
		web.Application.__init__(self, handlers, **settings)
if __name__ == "__main__":
	options.parse_command_line()
	server = httpserver.HTTPServer(Application())
	server.listen(options.port)
	ioloop.IOLoop.instance().start()