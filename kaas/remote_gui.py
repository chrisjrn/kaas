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

''' tkinter-based GUI for KAAS and the functionality exposed through
remote_server. The intention is to make it easy to start up a server and know
what the important information is.
'''

import atexit 
import os
import sys

from Tkinter import *

import remote_server
import keynote_script


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):

        # Create top-level frames

        self.path_frame = Frame(master=self)
        self.path_frame.pack(side="top", fill="x")

        self.server_frame = Frame(master=self)
        self.server_frame.pack(side="top", fill="x")

        self.pin_frame = Frame(master=self)
        self.pin_frame.pack(side="top", fill="x")

        self.version_picker_frame = Frame(master=self)
        self.version_picker_frame.pack(side="top", fill="x")

        self.button_frame = Frame(master=self)
        self.button_frame.pack(side="top", fill="x")

        # Shows where the server currently is

        self.path_label = Label(master=self.path_frame)
        self.path_label["text"] = "Press 'start serving' to begin."
        self.path_label.pack(side = "left")

        self.path_value = Label(master=self.path_frame)
        self.path_value["text"] = ""
        self.path_value.pack(side = "right")
        self.path_value["text"] = ""

        # Shows where the server currently is

        self.server_label = Label(master=self.server_frame)
        self.server_label["text"] = ""
        self.server_label.pack(side = "left")

        self.server_address = Label(master=self.server_frame)
        self.server_address["text"] = ""
        self.server_address.pack(side = "right")
        self.server_address["text"] = ""

        # Shows what the PIN number currently is

        self.pin_label = Label(master=self.pin_frame)
        self.pin_label["text"] = ""
        self.pin_label.pack(side = "left")

        self.pin_value = Label(master=self.pin_frame)
        self.pin_value["text"] = ""
        self.pin_value.pack(side = "right")

        # Shows a version picker

        self.version_picker_label = Label(master = self.version_picker_frame)
        self.version_picker_label["text"] = "Keynote version: "
        self.version_picker_label.pack(side = "left")

        picker_master = self.version_picker_frame
        self.keynote_version = StringVar(master = picker_master)
        OPTIONS = keynote_script.INSTALLED_VERSIONS.keys()
        self.keynote_version.set(OPTIONS[0]) # default value

        self.version_picker = apply(OptionMenu, (picker_master, self.keynote_version) + tuple(OPTIONS))
        self.version_picker.pack(side = "right", fill = "x")

        # Buttons

        self.start_serving_button = Button(master=self.button_frame)
        self.start_serving_button["text"] = "Start serving"
        self.start_serving_button["command"] = self.start_serving
        self.start_serving_button.pack(side = "top", fill = "x")

    def start_serving(self):

        keynote_script.select_version(self.keynote_version.get())

        self.prepare_show()

        pin = remote_server.generate_key()
        print >> sys.stderr, "Starting server..."
        address = remote_server.start_serving()

        self.server_label["text"] = "Now serving at: "
        self.server_address["text"] = "http://%s:%d" % address
        self.pin_label["text"] = "PIN number: "
        self.pin_value["text"] = pin

        self.start_serving_button["text"] = "Load new slideshow"
        self.start_serving_button["command"] = self.prepare_show

    def prepare_show(self):
        print >> sys.stderr, "Exporting slideshow..."
        remote_server.set_show()
        print >> sys.stderr, "Generating build previews..."
        remote_server.prepare_show()
        self.path_label["text"] = "Using slideshow: "
        self.path_value["text"] = os.path.basename(remote_server.get_show().path())


def stop_serving():
    remote_server.stop_serving()

atexit.register(stop_serving)


root = Tk()
app = Application(master=root)

app.master.title("KAAS Server")

app.mainloop()
root.destroy()

