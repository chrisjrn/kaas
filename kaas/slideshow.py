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

import keynote_script
import kpfutil
import kpfutil_v5

import os
import subprocess
import sys

class Slideshow(object):

    def __init__(self, path, kpfdir):
        self.__path__ = path
        self.__kpfdir__ = kpfdir
        # TODO Make this load from most appropriate KPF version
        self.__kpf__ = kpfutil_v5.KpfV5(kpfdir)

        # Variables for guessing where keynote is at the moment. Lol.
        self.current_build = 0 # Builds are 0-indexed
        self.current_slide = 1 # Slides are 1-indexed

        self.__build_count__ = self.__kpf__.build_count()
        self.__slide_count__ = self.__kpf__.slide_count()

    @property
    def build_count(self):
        return self.__build_count__

    @property
    def slide_count(self):
        return self.__slide_count__

    def path(self):
        ''' Returns the path to the keynote file used to generate this 
        Slideshow object '''
        return self.__path__

    def kpf(self):
        return self.__kpf__

    @property
    def hash(self):
        return self.__kpf__.hash

    ''' Lifecycle methods for slideshow '''

    def prepare(self):
        ''' Assembles all of the builds of the slides from the KPF transition
        information; at the conclusion of this, we'll have a series of slide builds
        '''
        builds_dir = os.path.join(self.__kpfdir__, "builds")
        os.mkdir(builds_dir)
        self.__kpf__.assemble_slides(builds_dir)
        
        self.first_builds = {}
        self.slides_by_first_event = {}
        for build, slide in self.__kpf__.navigator_events().items():
            self.first_builds[slide] = build
            self.slides_by_first_event[build] = slide

        self.prepared = True
        self.builds_dir = builds_dir

        
    def obliterate(self):
        ''' Deletes the exported slideshow; most of this object will be invalid
        from now on. '''
        subprocess.call(["rm", "-rf", self.__kpfdir__])

    ''' Methods for getting data to the consumer '''

    def notes(self, slide):
        ''' Gets presenter notes for the given slide '''
        return self.__kpf__.notes(slide)

    def build_preview(self, event):
        ''' Returns the filename for the build preview for the
        given event. Must be called AFTER self.prepare() -- this creates
        the build previews. '''

        assert(self.prepared)
        
        return os.path.join(self.builds_dir, "build_%d.jpg" % event)

    def build_for_slide(self, slide):
        ''' Returns the first build for the given slide. '''
        return self.first_builds[slide]

    def slide_for_build(self, build):
        ''' Returns the slide number for a given build '''
        build_keys = reversed(sorted(self.slides_by_first_event.keys()))
        for key in build_keys:
            if build >= key:
                return self.slides_by_first_event[key]


    def find_still_from(self, event):
        ''' Finds the first still event in the specified direction. '''

        i = event
        while self.__kpf__.build_is_autoplay(i) and i <= self.build_count:
            i += 1
        return i

    def keynote_is_playing(self):
        ''' Asks keynote if it is playing a slideshow '''
        is_playing = keynote_script.slide_show_is_playing().strip()
        return True if is_playing == "true" else False if is_playing == "false" else None
    
    def keynote_current_slide(self):
        ''' Asks keynote for its current slide '''
        current_slide = keynote_script.get_current_slide()
        return int(current_slide)

    ''' Methods for altering the state of the slideshow '''

    def start_slide_show(self):
        ''' Starts the slideshow; stops all builds. '''
        keynote_script.start_slide_show()
        slide = keynote_script.get_current_slide()
        keynote_script.go_to_slide(slide)

        self.current_slide = slide
        self.current_build = self.build_for_slide(slide)

    def start_or_resume(self):
        try:
            keynote_script.resume_slide_show()
        except:
            self.start_slide_show()

    def pause(self):
        keynote_script.pause_slide_show()

    def synchronise(self):
        ''' Resets the slideshow to the current slide, synchronsises
        the build counter appropriately '''
        slide = keynote_script.get_current_slide()
        keynote_script.go_to_slide(slide)

        self.current_slide = slide
        self.current_build = self.build_for_slide(slide)

    def previous(self):
        ''' Moves to the previous slide '''

        keynote_script.previous_build()
        self.current_build -= 1
        if self.current_build < 0:
            self.current_build = 0
        self.current_slide = self.slide_for_build(self.current_build)

    def next(self):
        ''' Moves to the next slide '''

        keynote_script.next_build()
        self.current_build += 1
        self.current_build = self.find_still_from(self.current_build)

        if self.current_build >= self.build_count:
            self.current_build = self.build_count - 1

        self.current_slide = self.slide_for_build(self.current_build)





def generate():
    ''' Asks keynote to export a KPF of the current slide show. 
    If so, we'll generate a Slideshow() and return it.'''

    out_dir = os.tmpnam()
    print >> sys.stderr, "Output: ", out_dir
    path = keynote_script.slide_show_path()
    output = keynote_script.export_slide_show(out_dir)
    output = output.strip()
    if output == "":
        return Slideshow(path, out_dir)
    else:
        # FAIL.
        return None


''' Demo script '''
if __name__ == "__main__":
    print >> sys.stderr, "Exporting slideshow: "
    slideshow = generate()

    if slideshow == None:
        print >> sys.stderr, "Failed to generate slideshow"
        sys.exit(1)

    print >> sys.stderr, "Preparing builds: "
    slideshow.prepare()

    #slideshow.start_slide_show()
    #slideshow.next()
    #slideshow.next()
    #slideshow.next()
    #slideshow.previous()
    #slideshow.next()

    print slideshow.current_slide
    print slideshow.current_build
    print slideshow.build_preview(slideshow.current_build)




    raw_input("press enter to proceed")

    slideshow.obliterate()