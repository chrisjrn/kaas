#!/usr/bin/env python

import keynote_script

import BaseHTTPServer
import subprocess

class RemoteHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			command = self.path.split("/")[-1]
			output = perform_request(command)
			self.send_response(200)
		except:
			output = ""
			self.send_response(500)

		self.send_header("Content-Type", "application/json")
		self.end_headers()
		print output
		#print >> self.wfile, self.path

		print >> self.wfile, output

class Handlers(object):
	''' Handlers for the various URLs '''

	def next(self):
		return keynote_script.next_build()

	def previous(self):
		return keynote_script.previous_build()


_HANDLERS = Handlers()

def perform_request(command):
	return _HANDLERS.__getattribute__(command)()


while True:
	BaseHTTPServer.HTTPServer(('', 8000), RemoteHTTPRequestHandler).handle_request()