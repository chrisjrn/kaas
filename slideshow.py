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

	def prepare(self):
		''' Assembles all of the builds of the slides from the KPF transition
		information; at the conclusion of this, we'll have a series of slide builds
		'''
		builds_dir = os.path.join(self.__kpfdir__, "builds")
		os.mkdir(builds_dir)
		self.__kpf__.assemble_slides(builds_dir)
		self.prepared = True

	def obliterate(self):
		subprocess.call(["rm", "-rf", self.__kpfdir__])



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

	raw_input("Press enter to proceed")

	slideshow.obliterate()