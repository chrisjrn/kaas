#!/usr/bin/env python

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
		return slide_change("show-slide-next.applescript")

	def previous(self):
		return slide_change("show-slide-previous.applescript")


_HANDLERS = Handlers()

def perform_request(command):
	return _HANDLERS.__getattribute__(command)()

def slide_change(script):
	output = subprocess.check_output(["/usr/bin/osascript", script])
	return output


while True:
	BaseHTTPServer.HTTPServer(('', 8000), RemoteHTTPRequestHandler).handle_request()