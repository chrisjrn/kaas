#!/usr/bin/env python2.6

import hashlib
import json
import sys
import os

from AppKit import NSBitmapImageRep
from AppKit import NSCompositeSourceOver
from AppKit import NSDeviceRGBColorSpace
from AppKit import NSGraphicsContext
from AppKit import NSImage
from AppKit import NSImageRep
from AppKit import NSJPEGFileType
from AppKit import NSMakeRect
from AppKit import NSPoint
from AppKit import NSSize
from AppKit import NSZeroRect

class Kpf(object):

    def __init__(self, filename):
        self.kpfdir = os.path.dirname(filename) # The directory where the textures can be found

        kpfjson  = open(filename).read()
        self.kpf = json.loads(kpfjson)

        h = hashlib.sha256()
        h.update(kpfjson)
        self.hash = h.hexdigest()


    def raw_kpf(self):
        return self.kpf

    def kpf_hash(self):
        return self.hash

    def assemble_slides(self, output_directory):
        assemble_slides(self, output_directory)


def assemble_slides(kpf, output_directory):

    for event_index, event in enumerate(kpf.kpf["eventTimelines"]):
        assemble_slide(kpf, output_directory, event_index, event)


def assemble_slide(kpf, output_directory, build_index, event):

    init = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_
    im = init(None, kpf.kpf["slideWidth"], kpf.kpf["slideHeight"], 8, 4, True, False, NSDeviceRGBColorSpace, 0, 0)

    for state_index, state in enumerate(event["eventInitialStates"]):
        if state["hidden"] != 0:
            continue
        add_texture(kpf, im, state)

    fn = os.path.join(output_directory, "build_%00000d.jpg" % (build_index))

    imjpeg = im.representationUsingType_properties_(NSJPEGFileType, None)
    imjpeg.writeToFile_atomically_(fn, False)


def add_texture(kpf, image, state):
    textures = kpf.kpf["textures"]
    transform = state["affineTransform"]
    texture_file = textures[state["texture"]]["url"]
    sx, n0, n1, sy, tx, ty = transform
    
    tex = NSImage.alloc().initWithContentsOfFile_(os.path.join(kpf.kpfdir, texture_file))

    # TODO: support opacity
    if (sx != 1 or sy != 1):
        #tex = tex.resize((sx, sy))
        tex.setSize_(NSSize(sx, sy))

    context = NSGraphicsContext.graphicsContextWithBitmapImageRep_(image)
    context.setCompositingOperation_(NSCompositeSourceOver)
    NSGraphicsContext.setCurrentContext_(context)

    # Cocoa uses inverted Y-axis...
    ty_ = image.size().height - tex.size().height - ty
    tex.drawAtPoint_fromRect_operation_fraction_(NSPoint(tx, ty_), NSZeroRect, NSCompositeSourceOver, 1.0)


#first_initial_transforms()
def main():
    kpffile = sys.argv[1]
    kpf = Kpf(kpffile)
    kpf.assemble_slides(sys.argv[2])

if __name__ == "__main__":
    main()



#print_animation_actions()