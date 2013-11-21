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

''' JSON endpoints for the KAAS server. '''

import json

def handle(path, show):

    status = 200
    try:
        output = Handlers(show).handle(path[1], path)
    except AttributeError:
        status = 404
        output = "No such path: " + "/".join(path)

    output_ucode = json.dumps(output, ensure_ascii = False, indent = 2).encode("UTF-8")
    return (status, "application/json; charset=UTF-8", output_ucode)


class Handlers(object):
    def __init__(self, show):

        self.show = show

    def handle(self, kw, path):
        func = self.__getattribute__(kw)
        return func(path)

    def slideshow_info(self, path):
        ''' Returns the basic information about the current slideshow '''
        info = {
            "slide_count" : self.show.slide_count,
            "build_count" : self.show.build_count,
            "first_builds" : self.show.first_builds,
            "hash" : self.show.hash,
        }
        return info

    def current_state(self, path):
        ''' Returns the current state of the slideshow in progress '''
        info = {
            "slide" : self.show.current_slide,
            "build" : self.show.current_build,
            "hash" : self.show.hash,
        }
        return info

    def notes(self, path):
        ''' Returns notes for specific slide, or every slide if not specified '''
        if len(path) >= 3 and path[2].strip() != "":
            return self.show.notes(int(path[2]))
        else:
            notes = {}
            for i in xrange(1, self.show.slide_count + 1):
                notes[i] = self.show.notes(i)
            return notes


    ''' Commands for remote-controlling keynote itself '''

    def next(self, path):
        ''' Shows the next slide, returns the current_state '''

        self.show.next()
        return self.current_state(path)

    def previous(self, path):
        ''' Shows the previous slide, returns the current_state '''

        self.show.previous()
        return self.current_state(path)

    def start(self, path):
        ''' Starts/resumes the slideshow, returns the current_state '''

        self.show.start_or_resume()
        return self.current_state(path)

    def pause(self, path):
        ''' Pauses the slideshow, returns the current_state '''

        self.show.pause()
        return self.current_state(path)



    def sync(self, path):
        ''' Syncs the server and the keynote slideshow, returns the current state '''

        self.show.synchronise()
        return self.current_state(path)

    ''' Method for interrogating the state of Keynote itself '''

    def monitor(self, path):
        out = { 
            "current_slide" : self.show.keynote_current_slide(),
            "is_playing" : self.show.keynote_is_playing(),
        }

        return out


