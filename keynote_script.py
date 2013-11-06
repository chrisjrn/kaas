#!/usr/bin/env python

import pipes
import subprocess

def export_slide_show(to_directory):
	''' Outputs a KPF at to_directory '''
	command = 'export front slideshow to "%s" as KPF_RAW' % (pipes.quote(to_directory))
	return __execute__(command)

def get_current_slide():
	return int(__execute__("slide number of current slide of front slideshow").strip())

def go_to_slide(slide):
	return __execute__("jump to slide %d of front slideshow" % slide)

def next_build():
	return __execute__("show next")

def previous_build():
	return __execute__("show previous")

def start_slide_show():
	return __execute__("start")

def __execute__(command):
	''' Gets keynote to execute the given applescript command '''
	to_run = 'tell application "Keynote" to %s' % command

	return subprocess.check_output(["osascript", "-e", to_run])