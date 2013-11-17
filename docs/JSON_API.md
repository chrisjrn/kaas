JSON API Documentation
======================

Authentication
--------------

See HTTP_DOCS


Endpoints
---------

### /json/slideshow_info

Returns the basic information about the current slideshow.

*Response Format*:

    {
        "slide_count" : kpf["slideCount"],
        "build_count" : len(kpf["eventTimelines"]),
        "first_builds" : self.show.first_builds,
        "hash" : self.show.kpf().kpf_hash(),
    }


### /json/current_state

Returns the current state of the slideshow in progress. This is a best guess
made by the server. The server may get out of sync if slide advance commands
are made directly with keynote and not through the server.

*Response Format*:

    {
        "slide" : self.show.current_slide,
        "build" : self.show.current_build,
        "hash" : self.show.kpf().kpf_hash(),
    }


### /json/monitor

Gets some key information about the slideshow from Keynote itself, rather than
the guess that is returned by current_state.

A key use case for this endpoint would be to compare the `current_slide` 
attribute with the `slide` attribute of `/json/current_state` to determine if
the server is out of sync. 

Note that during a long slide transition, Keynote will return the slide number
of the slide *before* the transition occurs; this means that the current_slide
value may occasionally not match with current_state (which will attempt to 
return the slide number after all automatic builds have finished).

*Response Format*:

    { 
        "current_slide" : self.show.keynote_current_slide(),
        "is_playing" : self.show.keynote_is_playing(),
    }


### /json/notes

Returns the notes for all slides in the deck.


### /json/notes/{slide_number}

Returns notes for a given slide number.


### /json/next

Asks Keynote to advance the slide show.

Returns the equivalent of `/json/current_state` AFTER the advance has been
called.


### /json/previous

Asks Keynote to go backwards in the slide show.

Returns the equivalent of `/json/current_state` AFTER the presentation has gone
backwards.


### /json/start

Attempts to resume the slideshow (if the show has been paused), or to start it
if a slideshow is not playing.

Returns the equivalent of `/json/current_state` AFTER the presentation has began
playing.


### /json/pause(self, path):

Pauses the slideshow if a slideshow is currently playing.

Returns the equivalent of `/json/current_state` AFTER the presentation has began
playing.


### /json/sync

Asks Keynote to synchronise itself to a known state in the slide show; resets
the values returned by current_state in the process.

This is done by asking keynote what slide it is currently showing, and then
resetting Keynote to the first build of that slide.

The key use of this call is to get the server in sync with Keynote if Keynote
is controlled from outside of the remote. This is because it's not possible to
ask Keynote how far it is through the builds of a given slide.

Returns the equivalent of `/json/current_state` AFTER the synchronisation has 
occurred.

