#!/usr/bin/env python2.6

# Copyright 2013 Christopher Neugebauer and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import json
import sys
import os

from collections import namedtuple

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

    def kpf_hash(self):
        ''' Identifies this specific slideshow. '''
        return NotImplemented

    def assemble_slides(self, output_directory):
        assemble_slides(self, output_directory)

    def build_count(self):
        return NotImplemented

    def build_is_autoplay(self, build):
        ''' Returns true is the build is an autoplay build '''
        return NotImplemented

    def navigator_events(self):
        ''' Returns a sparse array (dictionary) of the first
        builds for every slide '''
        return NotImplemented

    def notes(self, slide):
        ''' Returns the notes for the given slide '''
        return NotImplemented

    def texture(self, name):
        return NotImplemented


class KpfV5(Kpf):

    def __init__(self, kpfdir):
        self.kpfdir = kpfdir # The directory where the textures can be found
        filename = os.path.join(kpfdir, "kpf.json")

        kpfjson  = open(filename).read()
        self.kpf = json.loads(kpfjson)

        h = hashlib.sha256()
        h.update(kpfjson)
        self.hash = h.hexdigest()

    def build_count(self):
        return len(self.kpf["eventTimelines"])

    def build_is_autoplay(self, build):
        timelines = self.kpf["eventTimelines"]
        return timelines[build]["automaticPlay"] != 0

    def navigator_events(self):
        ''' Returns a sparse array (dictionary) of the first
        builds for every slide '''

        events = {}
        for item in self.kpf["navigatorEvents"]:
            slide = int(item["eventName"].split()[-1]) # Slide number. Yuck
            build = item["eventIndex"]
            events[build] = slide
        return events

    def notes(self, slide):
        try:
            return self.kpf["notes"]["slide-%d" % slide]
        except KeyError:
            # Slides without notes do not have a key in the notes
            # dictionary.
            return u""

    def raw_kpf(self):
        return self.kpf

    def kpf_hash(self):
        return self.hash

    def texture(self, name):
        return TextureV5(self, name)

class EventState(object):

    def texture(self):
        ''' Returns the texture that this event state applies to '''
        return NotImplemented

    def transform(self):
        ''' Returns the affine transform to be applied to the texture '''
        return NotImplemented

class Texture(object):

    def path(self):
        return NotImplemented

class EventStateV5(EventState):

    def __init__(self, kpf_v5, event_state_raw):
        self.kpf_v5 = kpf_v5
        self.event_state_raw = event_state_raw

    def texture(self):
        ''' Returns the texture that this event state applies to '''
        return TextureV5(self, self.kpf_v5, self.event_state_raw["texture"])

    def transform(self):
        ''' Returns the affine transform to be applied to the texture '''
        return self.event_state_raw["texture"]["affineTransform"]


class TextureV5(Texture):

    def __init__(self, kpf_v5, texture):
        self.texture = texture
        self.kpf_v5 = kpf_v5

    def path(self):
        textures = self.kpf_v5.raw_kpf()["textures"]
        texture_file = textures[self.texture]["url"]
        return os.path.join(self.kpf_v5.kpfdir, texture_file)

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
    #textures = kpf.kpf["textures"]
    transform = state["affineTransform"]
    #texture_file = textures[state["texture"]]["url"]
    texture = kpf.texture(state["texture"])

    sx, n0, n1, sy, tx, ty = transform
    
    tex = NSImage.alloc().initWithContentsOfFile_(texture.path())

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