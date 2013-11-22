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

import kpfutil

import hashlib
import json
import os


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


class BuildV6(kpfutil.Build):

    def __init__(self, kpf_v6, slide_index, build_raw):
        self.__kpf__ = kpf_v6
        self.build_raw = build_raw
        self.kpf_v6 = kpf_v6

    def __render__(self):
        for state in self.states():
            if state.is_hidden() != 0:
                continue
            sx, n0, n1, sy, tx, ty = state.transform()
            texture = state.texture()
            self.draw_texture(texture, (tx, ty), (sx, sy))


    def state(self, index):
        return EventStateV6(self.kpf_v6, self.build_raw["baseLayer"]["layers"][index])

    def state_count(self):
        return len(self.build_raw["baseLayer"]["layers"])

    def states(self):
        for i in xrange(self.state_count()):
            yield self.state(i)


class EventStateV6(object):

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


class TextureV6(kpfutil.Texture):

    def __init__(self, kpf_v6, slide_path, asset):
        self.kpf_v6 = kpf_v6
        self.slide_path = slide_path 
        self.asset = asset

    def path(self):
        return os.path.join(self.kpf_v6.kpfdir, self.slide_path, self.asset)

