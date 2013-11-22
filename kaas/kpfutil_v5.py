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

''' Implementation of the various classes in kpfutil.py for the Version 5
(iWork '09) RAW KPF format '''

import kpfutil

import hashlib
import json
import os

class KpfV5(kpfutil.Kpf):

    def __init__(self, kpfdir):
        self.kpfdir = kpfdir # The directory where the textures can be found
        filename = os.path.join(kpfdir, "kpf.json")

        kpfjson  = open(filename).read()
        self.kpf = json.loads(kpfjson)

        self.__width__ = self.kpf["slideWidth"]
        self.__height__ = self.kpf["slideHeight"]

        h = hashlib.sha256()
        h.update(kpfjson)
        self.__hash__ = h.hexdigest()

    def build(self, index):
        return BuildV5(self, self.kpf["eventTimelines"][index])

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

    def slide_count(self):
        return self.kpf["slideCount"]

    def texture(self, name):
        return TextureV5(self, name)


class BuildV5(kpfutil.Build):

    def __init__(self, kpf_v5, build_raw):
        self.build_raw = build_raw
        self.__kpf__ = kpf_v5
        self.kpf_v5 = kpf_v5
        self.initial_states_raw = build_raw["eventInitialStates"]

    def __render__(self):
        for state in self.states():
            if state.is_hidden() != 0:
                continue
            sx, n0, n1, sy, tx, ty = state.transform()
            texture = state.texture()
            self.draw_texture(texture, (tx, ty), (sx, sy))
    
    def state(self, index):
        return EventStateV5(self.kpf_v5, self.initial_states_raw[index])

    def states(self):
        for i in xrange(self.state_count()):
            yield self.state(i)

    def state_count(self):
        return len(self.initial_states_raw)


class EventStateV5(object):

    def __init__(self, kpf_v5, event_state_raw):
        self.kpf_v5 = kpf_v5
        self.event_state_raw = event_state_raw

    def is_hidden(self):
        return self.event_state_raw["hidden"] != 0

    def texture(self):
        ''' Returns the texture that this event state applies to '''
        return TextureV5(self.kpf_v5, self.event_state_raw["texture"])

    def transform(self):
        ''' Returns the affine transform to be applied to the texture '''
        return self.event_state_raw["affineTransform"]


class TextureV5(kpfutil.Texture):

    def __init__(self, kpf_v5, texture):
        self.texture = texture
        self.kpf_v5 = kpf_v5

    def path(self):
        textures = self.kpf_v5.kpf["textures"]
        texture_file = textures[self.texture]["url"]
        return os.path.join(self.kpf_v5.kpfdir, texture_file)
