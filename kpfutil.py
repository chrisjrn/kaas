#!/usr/bin/env python

import json
import sys
import os
from PIL import Image


class Kpf(object):

	def __init__(self, filename):
		self.kpfdir = os.path.dirname(filename) # The directory where the textures can be found
		self.kpf = json.load(open(filename))

	def assemble_slides(self, output_directory):
		assemble_slides(self, output_directory)


def assemble_slides(kpf, output_directory):

	for event_index, event in enumerate(kpf.kpf["eventTimelines"]):
		assemble_slide(kpf, output_directory, event_index, event)


def assemble_slide(kpf, output_directory, build_index, event):

	im = Image.new("RGBA", (kpf.kpf["slideWidth"], kpf.kpf["slideHeight"]))

	for state_index, state in enumerate(event["eventInitialStates"]):
		if state["hidden"] != 0:
			continue
		add_texture(kpf, im, state)

	fn = os.path.join(output_directory, "build_%00000d.jpg" % (build_index))
	im.save(fn)



def add_texture(kpf, image, state):
	textures = kpf.kpf["textures"]
	transform = state["affineTransform"]
	texture_file = textures[state["texture"]]["url"]
	sx, n0, n1, sy, tx, ty = transform
	tex = Image.open(os.path.join(kpf.kpfdir, texture_file))
	# TODO: support opacity
	if (sx != 1 or sy != 1):
		tex = tex.resize((sx, sy))
	if tex.mode == "RGBA":
		image.paste(tex, (tx, ty), tex)
	else:
		image.paste(tex, (tx, ty))


#first_initial_transforms()
def main():
	kpffile = sys.argv[1]
	kpf = Kpf(kpffile)
	kpf.assemble_slides(sys.argv[2])

if __name__ == "__main__":
	main()



#print_animation_actions()