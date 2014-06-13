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
from AppKit import NSPDFImageRep
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
            build.render(os.path.join(output_directory, "build_%00000d.jpg" % build_index))

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


class Build(object):

    _asset_cache = {}

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

        # Cache all assets so we don't frequently reload our PDFs.
        path = texture.path()
        if path in Build._asset_cache:
            tex = Build._asset_cache[path].copy()
        else:
            tex = NSImage.alloc().initWithContentsOfFile_(path)
            Build._asset_cache[path] = tex.copy()

        if isinstance(texture, TextureWithIndex):
            rep = tex.representations()[0]
            rep.setCurrentPage_(texture.index())

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


class Texture(object):

    def path(self):
        return NotImplemented

class TextureWithIndex(Texture):

    def index(self):
        return NotImplemented

def main():
    kpffile = sys.argv[1]
    kpf = KpfV5(kpffile)
    kpf.assemble_slides(sys.argv[1] + "/builds")


if __name__ == "__main__":
    main()
