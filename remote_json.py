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
