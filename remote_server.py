#!/usr/bin/env python

import remote_handler
import slideshow

import BaseHTTPServer
import subprocess
import sys

class RemoteHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			path = self.path.split('/')[1:]
			response, content_type, body = remote_handler.handle(path, show)

		except Exception as e:
			print >> sys.stderr, e
			self.fail()
			return

		self.send_response(response)
		self.send_header("Content-Type", content_type)
		self.end_headers()
		self.wfile.write(body)

	def fail(self):
		self.send_response(500)
		self.send_header("Content-Type", "text/plain")
		self.end_headers()
		#print >> self.wfile, self.path

		print >> self.wfile, "ERROR"

def serve_forever():
	while True:
		try:
			BaseHTTPServer.HTTPServer(('', 8000), RemoteHTTPRequestHandler).handle_request()
		except KeyboardInterrupt:
			show.obliterate()
			return


print >> sys.stderr, "Generating slideshow from frontmost keynote slideshow..."
show = slideshow.generate()
print >> sys.stderr, "Generating build previews..."
show.prepare()
print >> sys.stderr, "Now serving."
serve_forever()