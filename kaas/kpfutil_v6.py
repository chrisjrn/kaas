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

''' Implementation of the various classes in kpfutil.py for the Version 6
(iWork 2013) RAW KPF format '''

import keynote_script
import kpfutil

import hashlib
import json
import os
import zipfile

from collections import namedtuple
from xml.etree import ElementTree


class KpfV6(kpfutil.Kpf):

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

        self.__event_counter__ = 0
        self.__navigator_events__ = {}

        for _i, name in enumerate(slide_file_names):
            i = _i + 1
            slide_file = os.path.join(kpfdir, name, name+".json")
            raw_slide = json.load(open(slide_file))
            self.__raw_slides__[i] = raw_slide
            self.__process_slide__(i, name, raw_slide)

        self.generate_notes()

    def __process_slide__(self, index, name, raw_slide):
        for filename, asset in raw_slide["assets"].items():
            if "index" in asset:
                tex = TextureV6PDF(self, name, asset["url"], asset["index"])
            else:
                tex = TextureV6(self, name, asset["url"])
            self.__textures__[filename] = tex

        self.__navigator_events__[self.__event_counter__] = index
        for event in raw_slide["events"]:
            self.__event_counter__ += 1
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
        return self.__navigator_events__

    def notes(self, slide):
        ''' Returns the notes for the given slide '''
        return self.__notes__[slide]

    def slide_count(self):
        return self.kpf["slideCount"] 

    def texture(self, name):
        return self.__textures__[name]

    ''' Further functionality '''

    def generate_notes(self):
        ''' Generates the presenter notes for the current document. Sadly, keynote
        2013 doesn't provide a simple API for getting notes (yet), so this code
        does an export to the Keynote 2009 file format, and manually extracts the
        notes that way. Sorry.'''

        f = os.path.join(self.kpfdir, "classic.key")
        keynote_script.export_classic(f)

        z = zipfile.ZipFile(f)
        axpl = z.open("index.apxl")

        tree = ElementTree.parse(axpl)

        self.__notes__ = {}

        for slide, i in enumerate(tree.find("{http://developer.apple.com/namespaces/keynote2}slide-list")):
            text = ""
            for j in i.find("{http://developer.apple.com/namespaces/keynote2}notes"):
                text += "".join(itertext(j)).strip()
            self.__notes__[slide + 1] = text


class BuildV6(kpfutil.Build):

    def __init__(self, kpf_v6, slide_index, build_raw):
        self.__kpf__ = kpf_v6
        self.build_raw = build_raw
        self.kpf_v6 = kpf_v6

    def __render__(self):
        self.base_layer().draw((0,0))

    def base_layer(self):
        return LayerV6(self.kpf_v6, self, self.build_raw["baseLayer"])


class LayerV6(object):

    def __init__(self, kpf_v6, build, layer_raw):
        self.kpf_v6 = kpf_v6
        self.build = build
        self.layer_raw = layer_raw

    def draw(self, position):

        if not isinstance(position, point):
            position = point(*position)

        state = self.layer_raw["initialState"]

        # Only draw non-hidden layers
        if state["hidden"]:
            return

        _anchor = point_kpf(state["anchorPoint"])
        height = state["height"]
        width = state["width"]

        # anchorPoint is speficied as fraction of size, let's reify that.
        anchor = point(x = _anchor.x * width, y = _anchor.y * height)

        _pos = point_kpf(state["position"])
        
        # position is provided with the anchor point added. eek.
        pos = point(x = _pos.x - anchor.x, y = _pos.y - anchor.y)

        # real pos = pos in overall pic, so we can render.
        real_pos = point(pos.x + position.x, pos.y + position.y)

        for _layer in self.layer_raw["layers"]:
            layer = LayerV6(self.kpf_v6, self.build, _layer)
            layer.draw(real_pos)

        if "texture" in self.layer_raw:
            texture = self.kpf_v6.texture(self.layer_raw["texture"])
            self.build.draw_texture(texture, real_pos, (1, 1))



class TextureV6(kpfutil.Texture):

    def __init__(self, kpf_v6, slide_path, asset):
        self.kpf_v6 = kpf_v6
        self.slide_path = slide_path 
        self.asset = asset

    def path(self):
        return os.path.join(self.kpf_v6.kpfdir, self.slide_path, self.asset)

class TextureV6PDF(kpfutil.TextureWithIndex):

    def __init__(self, kpf_v6, slide_path, asset, index):
        self.kpf_v6 = kpf_v6
        self.slide_path = slide_path 
        self.asset = asset
        self._index = index

    def path(self):
        # PDF assets are stored in the root directory of the KPF. Just to confuse you.
        return os.path.join(self.kpf_v6.kpfdir, self.asset)

    def index(self):
        return self._index


point = namedtuple("point", ["x", "y"])

def point_kpf(pt):
    return point(x = pt["pointX"], y = pt["pointY"])


def itertext(self):
    tag = self.tag
    if not isinstance(tag, str) and tag is not None:
        return
    if self.text:
        yield self.text
    for e in self:
        for s in itertext(e):
            yield s
        if e.tail:
            yield e.tail

