#!/usr/bin/env python2.6

import remote_handler
import slideshow

import BaseHTTPServer
import SocketServer
import socket
import subprocess
import sys
import threading


''' Code for running the keynote remote server. This is pretty inherently
singleton at the moment, and it doesn't make much sense to do otherwise --
keynote can only display a single slide show at once anyway.

Exporting a new show will will disable the server for a while, but update
will happen in place '''

class ServerState(object):
    
    def __init__(self):
        self.show = None # No show until one is generated.
        self.server = None # No server yet.

STATE = ServerState()

class KeymoteHTTPServer(BaseHTTPServer.HTTPServer):
    pass

class RemoteHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            path = self.path.split('/')[1:]
            response, content_type, body = remote_handler.handle(path, STATE.show)

        except Exception as e:
            self.fail(e)
            raise e

        self.send_response(response)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)

    def fail(self, exception):
        self.send_response(500)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        #print >> self.wfile, self.path

        print >> self.wfile, exception

def create_server():
    #socket.error: [Errno 48] Address already in use
    port = 8000
    ip = socket.gethostbyname(socket.gethostname())
    while True:
        try:
            STATE.server = KeymoteHTTPServer(('', port), RemoteHTTPRequestHandler)
            break
        except socket.error as e:
            if e.errno == 48:
                # 48 := port in use.
                port += 1
            else:
                raise e
    return (ip, port)


def serve_forever():
    try:
        STATE.server.serve_forever()
    finally:
        print >> sys.stderr, "Obliterating slideshow..."
        STATE.show.obliterate()

def set_show():
    if STATE.show is not None:
        STATE.show.obliterate()

    STATE.show = None # Cannot serve anything for now
    STATE.show = slideshow.generate()

def prepare_show():
    if STATE.show is not None:
        STATE.show.prepare()

def start_serving():
    #STATE.server = create_server()
    address = create_server()
    server_thread = threading.Thread(target = serve_forever)
    server_thread.daemon = True
    server_thread.start()

    return address

def stop_serving():
    STATE.server.shutdown()

def main():
    print >> sys.stderr, "Generating export from frontmost keynote slideshow..."
    set_show()
    print >> sys.stderr, "Generating build previews..."
    prepare_show()
    print >> sys.stderr, "Starting server..."
    address = start_serving()
    print >> sys.stderr, "Now serving on: http://%s:%d" % (address)

    try:
        while True:
            raw_input()
    finally:
        stop_serving()

if __name__ == "__main__":
    main()