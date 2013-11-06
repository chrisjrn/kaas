#!/usr/bin/env python

import keynote_script
import kpfutil

import os
import subprocess
import sys

class Slideshow(object):

	def __init__(self, kpfdir):
		self.__kpfdir__ = kpfdir
		self.__kpf__ = kpfutil.Kpf(os.path.join(kpfdir, "kpf.json"))

		# Variables for guessing where keynote is at the moment. Lol.
		self.current_build = 0 # Builds are 0-indexed
		self.current_slide = 1 # Slides are 1-indexed
		self.certain = False   # Are we certain that current_build is correct?

	''' Lifecycle methods for slideshow '''

	def prepare(self):
		''' Assembles all of the builds of the slides from the KPF transition
		information; at the conclusion of this, we'll have a series of slide builds
		'''
		builds_dir = os.path.join(self.__kpfdir__, "builds")
		os.mkdir(builds_dir)
		self.__kpf__.assemble_slides(builds_dir)
		self.prepared = True
		self.builds_dir = builds_dir

	def obliterate(self):
		''' Deletes the exported slideshow; most of this object will be invalid
		from now on. '''
		subprocess.call(["rm", "-rf", self.__kpfdir__])

	''' Methods for getting data to the consumer '''

	def notes(self, slide):
		''' Gets presenter notes for the given slide '''
		return self.__kpf__["notes"]["slide-%d" % slide]

	def build_preview(self, event):
		''' Returns the filename for the build preview for the
		given event. Must be called AFTER self.prepare() -- this creates
		the build previews. '''

		assert(self.prepared)
		
		return os.path.join(self.builds_dir, "build_%d.jpg" % event)

	def find_next_still(self, event):
		''' Finds the next event that will be displayed after the given event '''

		i = event + 1
		timelines = self.__kpf__["eventTimelines"]
		while timelines[i]["automaticPlay"] != 0 and i <= len(timelines):
			i += 1
		return 1


def generate():
	# Asks keynote to export a KPF of the current slide show. 
	# If so, we'll generate Slideshow() and return it.

	out_dir = os.tmpnam()
	print >> sys.stderr, "Output: ", out_dir
	output = keynote_script.export_slide_show(out_dir)
	output = output.strip()
	if output == "":
		return Slideshow(out_dir)
	else:
		# FAIL.
		return None


if __name__ == "__main__":
	print >> sys.stderr, "Exporting slideshow: "
	slideshow = generate()

	if slideshow == None:
		print >> sys.stderr, "Failed to generate slideshow"
		sys.exit(1)

	print >> sys.stderr, "Preparing builds: "
	slideshow.prepare()

	k = keynote_script()

	# Go to given slide; show filename for still for where screen will stop.


	raw_input("Press enter to proceed")

	slideshow.obliterate()