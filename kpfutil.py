#!/usr/bin/env python

import json
import sys
import os
from PIL import Image

kpffile= sys.argv[1]

kpf = json.load(open(kpffile))
kpfdir = os.path.dirname(kpffile)


def print_slide_assembly():
	for event_index, event in enumerate(kpf["eventTimelines"]):

		for state_index, state in enumerate(event["eventInitialStates"]):

			texture = state["texture"]
			print event_index, state_index, kpf["textures"][texture]["url"]

def first_initial_transforms():
	for event_index, event in enumerate(kpf["eventTimelines"]):

		state = event["eventInitialStates"][0]

		transform = state["affineTransform"]
		print transform



def assemble_slides():

	for event_index, event in enumerate(kpf["eventTimelines"]):
		assemble_slide(event_index, event)


def assemble_slide(build_index, event):
	textures = kpf["textures"]

	im = None

	for state_index, state in enumerate(event["eventInitialStates"]):
		if state["hidden"] != 0:
			continue
		texture = textures[state["texture"]]["url"]
		if im == None:
			#print "boop"
			im = Image.open(os.path.join(kpfdir,texture))
		else:
			add_texture(im, texture, state["affineTransform"])
			pass

	fn = "build_%000d.png" % (build_index + 1)
	im.save(fn)



def add_texture(image, texture, transform):
	tx, n0, n1, ty, sx, sy = transform
	tex = Image.open(os.path.join(kpfdir,texture))
	if (tx != 1 or ty != 1):
		tex = tex.resize((tx, ty))
	if tex.mode == "RGBA":
		image.paste(tex, (sx, sy), tex)
	else:
		image.paste(tex, (sx, sy))



#first_initial_transforms()
assemble_slides()



#print_animation_actions()