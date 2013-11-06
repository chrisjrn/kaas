#!/usr/bin/env python

import pipes
import subprocess

def export_slide_show(to_directory):
	# export front slideshow to (item 1 of argv) as KPF_RAW
	command = 'export front slideshow to "%s" as KPF_RAW' % (pipes.quote(to_directory))
	return __execute__(command)


def get_current_slide():
	pass

def go_to_slide(slide):
	return __execute__("show slide %d of front slideshow" % slide)

def start_slide_show():
	return __execute__("start")

def __execute__(command):
	to_run = 'tell application "Keynote" to %s' % command

	return subprocess.check_output(["osascript", "-e", to_run])