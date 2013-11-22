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

import pdb

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

    @property
    def hash(self):
        ''' Identifies this specific slideshow. '''
        return self.__hash__

    def assemble_slides(self, output_directory):
        ''' Outputs all build previews into the output directory '''
        for build_index, build in enumerate(self.builds()):
            build.render(os.path.join(output_directory, "build_%00000d" % build_index))

    def build(self, index):
        ''' Returns the index-th build of the slideshow '''
        return NotImplemented

    def build_count(self):
        ''' Returns the number of builds in the slideshow '''
        return NotImplemented

    def builds(self):
        ''' Iterator for all of the builds in the slideshow '''
        for i in xrange(self.build_count()):
            yield self.build(i)

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

    def slide_count(self):
        ''' Returns the number of slides in the slideshow '''
        return NotImplemented

    def texture(self, name):
        ''' Returns a Texture object, as keyed by the name

        name: the internal KPF name for the texture. The meaning
        of name depends on the implementation '''
        return NotImplemented

    @property
    def height(self):
        ''' The global height of the slideshow '''
        return self.__height__

    @property
    def width(self):
        ''' The global width of the slideshow '''
        return self.__width__


class KpfV6(Kpf):

    def __init__(self, kpfdir):
        self.kpfdir = kpfdir # The directory where the textures can be found
        filename = os.path.join(kpfdir, "header.json")

        kpfjson  = open(filename).read()
        self.kpf = json.loads(kpfjson)

        self.__width__ = self.kpf["slideWidth"]
        self.__height__ = self.kpf["slideHeight"]

        h = hashlib.sha256()
        h.update(kpfjson)
        self.__hash__ = h.hexdigest()

        slide_file_names = self.kpf["slideList"]
        self.__raw_slides__ = {}
        self.__builds__ = []
        self.__textures__ = {}
        for _i, name in enumerate(slide_file_names):
            i = _i + 1
            slide_file = os.path.join(kpfdir, name, name+".json")
            raw_slide = json.load(open(slide_file))
            self.__raw_slides__[i] = raw_slide
            self.__process_slide__(i, name, raw_slide)

    def __process_slide__(self, index, name, raw_slide):
        for filename, asset in raw_slide["assets"].items():
            self.__textures__[filename] = TextureV6(self, name, asset["url"])

        for event in raw_slide["events"]:
            build = BuildV6(self, index, event)
            self.__builds__.append(build)


    def build(self, index):
        return self.__builds__[index]

    def build_count(self):
        return len(self.__builds__)

    def build_is_autoplay(self, build):
        ''' Returns true is the build is an autoplay build '''
        return self.__builds__[build].build_raw["automaticPlay"]

    def navigator_events(self):
        ''' Returns a sparse array (dictionary) of the first
        builds for every slide '''
        return {}

    def notes(self, slide):
        ''' Returns the notes for the given slide '''
        return ""

    def slide_count(self):
        return self.kpf["slideCount"] 

    def texture(self, name):
        return self.__textures__[name]

class Build(object):

    def render(self, filename):
        ''' Renders the given build's build preview to an image 
        with the given filename.
        '''

        # Sets up a blank bitmap canvas for drawing to. Such an ugly method
        # call. Any easier way to do this in Obj-C?
        init = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_
        im = init(None, self.kpf.width, self.kpf.height, 8, 4, True, False, NSDeviceRGBColorSpace, 0, 0)

        # Set up the Objective-C graphics context based on the bitmap canvas
        # we just created
        context = NSGraphicsContext.graphicsContextWithBitmapImageRep_(im)
        context.setCompositingOperation_(NSCompositeSourceOver)
        NSGraphicsContext.setCurrentContext_(context)

        # Ask the implementation to render itself
        self.__render__()

        # Output the file
        imjpeg = im.representationUsingType_properties_(NSJPEGFileType, None)
        imjpeg.writeToFile_atomically_(filename, False)

    def __render__(self):
        ''' Version-specific method for rendering this build.
        Will be called by self.render(). '''
        return NotImplemented

    def draw_texture(self, texture, location, scale):
        ''' Draws the texture into this build's graphics context
        at the location, to the given scale.

        self.render() needs to a call parent of this method, in order
        to set up the Cocoa graphics context for the draw calls to work

        texture: a Texture object
        location: (tx, ty) tuple
        scale: (sx, sy) tuple
        '''

        tx, ty = location
        sx, sy = scale
        
        tex = NSImage.alloc().initWithContentsOfFile_(texture.path())

        # TODO: support opacity
        if (sx != 1 or sy != 1):
            #tex = tex.resize((sx, sy))
            tex.setSize_(NSSize(sx, sy))

        # Cocoa uses inverted Y-axis...
        ty_ = self.kpf.height - tex.size().height - ty
        tex.drawAtPoint_fromRect_operation_fraction_(NSPoint(tx, ty_), NSZeroRect, NSCompositeSourceOver, 1.0)

    @property
    def kpf(self):
        ''' Returns the KPF object that this build belongs to '''
        return self.__kpf__


class EventState(object):

    def is_hidden(self):
        ''' Is this event state hidden? '''
        return NotImplemented

    def texture(self):
        ''' Returns the texture that this event state applies to '''
        return NotImplemented

    def transform(self):
        ''' Returns the affine transform to be applied to the texture '''
        return NotImplemented


class Texture(object):

    def path(self):
        return NotImplemented


class BuildV6(Build):

    def __init__(self, kpf_v6, slide_index, build_raw):
        self.build_raw = build_raw
        self.kpf_v6 = kpf_v6

    def state(self, index):
        return EventStateV6(self.kpf_v6, self.build_raw["baseLayer"]["layers"][index])

    def state_count(self):
        return len(self.build_raw["baseLayer"]["layers"])


class EventStateV6(EventState):

    def __init__(self, kpf_v6, event_state_raw):
        self.kpf_v6 = kpf_v6
        self.event_state_raw = event_state_raw


    def is_hidden(self):
        ''' Is this event state hidden? '''
        return self.event_state_raw["initialState"]["hidden"] != 0

    def texture(self):
        ''' Returns the texture that this event state applies to '''
        texture = self.find_texture(self.event_state_raw) #["layers"][0]["texture"]
        return self.kpf_v6.texture(texture)

    def transform(self):
        ''' Returns the affine transform to be applied to the texture '''
        return self.event_state_raw["layers"][0]["initialState"]["affineTransform"]

    def find_texture(self, dc):
        if "texture" in dc:
            return dc["texture"]
        if "layers" in dc:
            return self.find_texture(dc["layers"][0])


class TextureV6(Texture):

    def __init__(self, kpf_v6, slide_path, asset):
        self.kpf_v6 = kpf_v6
        self.slide_path = slide_path 
        self.asset = asset

    def path(self):
        return os.path.join(self.kpf_v6.kpfdir, self.slide_path, self.asset)


def main():
    kpffile = sys.argv[1]
    kpf = KpfV5(kpffile)
    kpf.assemble_slides(sys.argv[1] + "/builds")


if __name__ == "__main__":
    main()
