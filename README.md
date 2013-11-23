KAAS: Keynote as a Service
==========================

Introduction
------------

KAAS is a HTTP server for controlling compatible versions of Apple's Keynote 
presentation software via HTTP. It exposes a JSON API for determining the current
slide and build progress, for starting, pausing, and controlling the current
slide show.

It can also send notes and build previews to client devices.

This functionality is also exposed in a basic HTML client, which will be 
extended and documented in the future.

The server is written in Python 2.6+, and has a dependency on PyObjC & AppKit.
Note that the default interpreter is Python 2.6 as this provices PyObjC 
bindings on most Mac OS X installations with no external dependencies.

It currently has very good support for Keynote version 5 (iWork 2009), and has 
experimental-quality support for Keynote version 6 (iWork 2013) -- the quality
of scripting interface is currently far lower in Keynote 6.

This is the server component of Keymote, my Android Keynote Remote, which can
be found on the [Play Store](https://play.google.com/store/apps/details?id=net.noogz.keymote)
(restricted to approved testing users only).


Basic use -- Command Line
-------------------------

Before you can load the server, you'll need to start Keynote up, and open a
presentation file. If you have multiple presentation files open, make sure the
file you want to present from is front-most.

To load up the server, run

    $ ./kaas/remote_server.py

The server will output the following:

    Generating export from frontmost keynote slideshow...
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

### Troubleshooting

If you get an `ImportError: No module named AppKit` message; try running the following:

    $ sudo easy_install-2.6 pyobjc-framework-Cocoa

And running 

    $ python2.6 kaas/remote_server.py


Basic Use -- GUI
----------------

From your command line, run

    $ ./kaas/remote-gui.py


JSON API Documentation
----------------------

Once API documentation is ready, it'll be available at JSON_API.md.


App & Module Structure
----------------------

### `kaas/`

- keynote_script.py -- Low-level python-to-Applescript bridge for keynote, 
  exposes functions needed for controlling keynote.
- kpfutil.py -- Abstract interface for manipulating Keynote's JSON export formats, 
  including assembling build previews from its degenerate textures. 
- kpfutil_v5.py -- Low-level details for manipulating Keynote 5/iWork '09 JSON exports.
  See kpf-json-format.txt for my notes on how the format works.
- kpfutil_v6.py -- Low-level details for manipulating Keynote 6/iWork 2013 JSON exports.
- remote_handler.py -- The GET request handler for the server.
- remote_gui.py -- TK-based GUI for KAAS.
- remote_json.py -- Handler for JSON API calls.
- remote_server.py -- The HTTP server for KAAS. This also handles authentication
  of requests before passing them off to the handler.
- slideshow.py -- A higher-level API for manipulating KPF files and controlling
  keynote than either kpfutil.py or keynote_script.py respectively.

### `docs/`:

- kpf-json.format.txt -- Vague notes I wrote when trying to understand the KPF
  (Keynote JSON) format that KAAS uses to understand the presentation being 
  played.


Licence
-------

Copyright 2013 Christopher Neugebauer and contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.