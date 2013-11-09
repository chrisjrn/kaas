#!/usr/bin/env python2.6

import keynote_script
import kpfutil

import os
import subprocess
import sys

class Slideshow(object):

    def __init__(self, kpfdir):
        self.__kpfdir__ = kpfdir
        self.__kpf__ = kpfutil.Kpf(os.path.join(kpfdir, "kpf.json"))

        # Variables for guessing where keynote is at the moment. Lol.
        self.current_build = 0 # Builds are 0-indexed
        self.current_slide = 1 # Slides are 1-indexed

        self.build_count = len(self.__kpf__.kpf["eventTimelines"])

    def kpf(self):
        return self.__kpf__

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
        for item in self.__kpf__.kpf["navigatorEvents"]:
            slide = int(item["eventName"].split()[-1]) # Slide number. Yuck
            self.first_builds[slide] = item["eventIndex"]
            self.slides_by_first_event[item["eventIndex"]] = slide

        self.prepared = True
        self.builds_dir = builds_dir

        
    def obliterate(self):
        ''' Deletes the exported slideshow; most of this object will be invalid
        from now on. '''
        subprocess.call(["rm", "-rf", self.__kpfdir__])

    ''' Methods for getting data to the consumer '''

    def notes(self, slide):
        ''' Gets presenter notes for the given slide '''
        try:
            return self.__kpf__.kpf["notes"]["slide-%d" % slide]
        except KeyError:
            # Slides without notes do not have a key in the notes
            # dictionary.
            return u""

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


    def find_still_from(self, event, direction = 1):
        ''' Finds the first still event in the specified direction. '''

        i = event
        timelines = self.__kpf__.kpf["eventTimelines"]
        while timelines[i]["automaticPlay"] != 0 and i <= len(timelines):
            i += direction
        return i

    ''' Methods for altering the state of the slideshow '''

    def start_slide_show(self):
        ''' Starts the slideshow; stops all builds. '''
        keynote_script.start_slide_show()
        slide = keynote_script.get_current_slide()
        keynote_script.go_to_slide(slide)

        self.current_slide = slide
        self.current_build = self.build_for_slide(slide)

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
    output = keynote_script.export_slide_show(out_dir)
    output = output.strip()
    if output == "":
        return Slideshow(out_dir)
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

    slideshow.start_slide_show()
    slideshow.next()
    slideshow.next()
    slideshow.next()
    slideshow.previous()
    slideshow.next()

    print slideshow.current_slide
    print slideshow.current_build
    print slideshow.build_preview(slideshow.current_build)




    raw_input("press enter to proceed")

    slideshow.obliterate()