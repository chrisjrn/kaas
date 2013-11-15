KAAS: Keynote as a Service
==========================

Introduction
------------

KAAS is a HTTP server for controlling compatible versions of Apple's Keynote 
presentation software via HTTP. It exposes a JSON API for determining the current
slide and build progress, for starting, pausing, and controlling the current
slide show.

It can also send notes and build previews to client devices.

The server is written in Python 2.6+, and has a dependency on PyObjC & AppKit.
Note that the default interpreter is Python 2.6 as this provices PyObjC 
bindings on most Mac OS X installations with no external dependencies.

It currently does not support Keynote 6 (2013 release), due to Keynote 6's 
lack of a scripting interface.

This is the server component of Keymote, my Android Keynote Remote, which can
be found on the (Play Store)[https://play.google.com/store/apps/details?id=net.noogz.keymote].


Basic use -- Command Line
-------------------------

Before you can load the server, you'll need to start Keynote up, and open a
presentation file. If you have multiple presentation files open, make sure the
file you want to present from is front-most.

To load up the server, run

    $ ./remote_server.py

The server will output the following:

    Generating build previews...
    Starting server...
    Now serving on: http://192.168.1.71:8000
    The PIN number is: 123456

Direct your Keynote Remote app at the listed server, and enter the PIN number.
The PIN number is used to authenticate API calls made from the app -- this 
means that randoms can't take over your presentation. But you really should be using
this on a private network. Really :)

If you want to present from a different deck of slides, you will need to quit 
the server (Ctrl+C), and restart it. The ability to change slide decks is a
planned feature.


Basic Use -- GUI
----------------

A graphical user interface for running the server is planned.


JSON API Documentation
----------------------

Once API documentation is ready, it'll be available at JSON_API.md.


App & Module Structure
----------------------

- keynote_script.py -- Low-level python-to-Applescript bridge for keynote, 
  exposes functions needed for controlling keynote.
- kpfutil.py -- Low-level tools for manipulating Keynote's JSON export format, 
  including assembling build previews from its degenerate textures. See 
  kpf-json-format.txt for my notes on how the format works.
- remote_handler.py -- The GET request handler for the server.
- remote_json.py -- Handler for JSON API calls.
- remote_server.py -- The HTTP server for KAAS. This also handles authentication
  of requests before passing them off to the handler.
- slideshow.py -- A higher-level API for manipulating KPF files and controlling
  keynote than either kpfutil.py or keynote_script.py respectively.

Also of interest:

- kpf-json.format.txt -- Vague notes I wrote when trying to understand the KPF
  (Keynote JSON) format that KAAS uses to understand the presentation being 
  played.


Licence
-------

Copyright 2013 Christopher Neugebauer

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.