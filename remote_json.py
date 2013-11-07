#!/usr/bin/env python

import json

def handle(path, show):

	output = Handlers(show).handle(path[1], path)

	return (200, "application/json", json.dumps(output, ensure_ascii = False, indent = 2))


class Handlers(object):
	def __init__(self, show):

		self.show = show

	def handle(self, kw, path):
		func = self.__getattribute__(kw)
		return func(path)

	def slideshow_info(self, path):
		''' Returns the basic information about the current slideshow '''
		kpf = self.show.kpf().raw_kpf()
		info = {
			"slide_count" : kpf["slideCount"],
			"build_count" : len(kpf["eventTimelines"]),
			"first_builds" : self.show.first_builds
		}
		return info

	def current_state(self, path):
		''' Returns the current state of the slideshow in progress '''
		info = {
			"slide" : self.show.current_slide,
			"build" : self.show.current_build,
		}
		return info

	''' Commands for remote-controlling keynote itself '''

	def next(self, path):
		''' Shows the next slide, returns the current_state '''

		self.show.next()
		return self.current_state(path)

	def previous(self, path):
		''' Shows the previous slide, returns the current_state '''

		self.show.previous()
		return self.current_state(path)

	def start(self, path):
		''' Starts the slideshow, returns the current_state '''

		self.show.start_slide_show()
		return self.current_state(path)

	def sync(self, path):
		''' Syncs the server and the keynote slideshow, returns the current state '''

		self.show.synchronise()
		return self.current_state(path)

