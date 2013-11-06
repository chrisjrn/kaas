#!/usr/bin/env python

import kpfutil

import os
import subprocess
import sys

class Slideshow(object):

	def obliterate(self):
		pass



def generate():
	# Asks keynote to export a KPF of the current slide show. 
	# If so, we'll generate Slideshow() and return it.

	out_dir = os.tmpnam()
	print >> sys.stderr, "Output: ", out_dir
	output = subprocess.check_output(["osascript", "export-kpf.applescript", out_dir])
	output = output.strip()
	if output == "0":
		return Slideshow()
	else:
		# FAIL.
		return None


if __name__ == "__main__":
	slideshow = generate()

	raw_input("Press enter to proceed")

	slideshow.obliterate()