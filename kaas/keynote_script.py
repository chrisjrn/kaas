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

import os
import pipes
import subprocess

''' AppleScript commands for given minimum versions of Keynote '''
COMMANDS = {}

COMMANDS["5.0"] = {
    'export_slide_show' : 'export front slideshow to "%s" as KPF_RAW',
    'get_current_slide' : 'slide number of current slide of front slideshow', 
    'go_to_slide' : 'show slide %d of front slideshow',
    'next_build' : 'show next',
    'pause_slide_show' : 'pause slideshow',
    'previous_build' : 'show previous',
    'resume_slide_show' : 'resume slideshow',
    'slide_show_is_playing' : 'playing',
    'slide_show_path' : 'path of front slideshow',
    'start_slide_show' : 'start',
}

COMMANDS["6.0"] = {
    'export_classic' : 'export front document to POSIX file "%s" as Classic',
    'export_slide_show' : 'export front document to POSIX file "%s" as HTML with properties {rawKPF : true}',
    'get_current_slide' : 'slide number of current slide of front slideshow', 
    'go_to_slide' : 'show slide %d of front slideshow',
    'next_build' : 'show next',
    'pause_slide_show' : 'stop front document',
    'previous_build' : 'show previous',
    'resume_slide_show' : 'start front document', # resume will *always* fail for the moment
    'slide_show_is_playing' : 'playing',
    'slide_show_path' : 'name of front document', # TODO get a better response here.
    'start_slide_show' : 'start front document',
}


def select_version(version = None, excluded = set()):
    global COMMANDS_VERSION
    global APPLICATION_VERSION

    useable_versions = set(INSTALLED_VERSIONS) - excluded

    if version == None:
        version_to_try = max(useable_versions)
        try:
            select_version(version_to_try)
            return
        except KeyError:
            new_excluded = excluded | set([version_to_try])
            available = useable_versions - new_excluded
            if len(available) > 0:
                select_version(None, new_excluded)
                return
        raise KeyError("No suitable version of Keynote installed")

    else:
        _version = version
        version = __version_tuple__(version)
        
        installs_matching_major_version = (j for j in 
            (__version_tuple__(i) for i in COMMANDS) if j[0] == version[0])

        for install in installs_matching_major_version:
            version_greater_than_install = (i >= j for i,j in zip(version, install))
            if False not in version_greater_than_install:
                COMMANDS_VERSION = ".".join(str(i) for i in install)
                APPLICATION_VERSION = ".".join(str(i) for i in version)
                return

        raise KeyError("No keynote app found for specified version")

def export_slide_show(to_directory):
    ''' Outputs a KPF at to_directory '''
    command = COMMANDS[COMMANDS_VERSION]['export_slide_show'] % (pipes.quote(to_directory))
    return __execute__(command)

def export_classic(to_file):
    ''' Outputs a classic keynote file at to_directory '''
    command = COMMANDS[COMMANDS_VERSION]['export_classic'] % (pipes.quote(to_file))
    return __execute__(command)

def get_current_slide():
    return int(__execute__(COMMANDS[COMMANDS_VERSION]['get_current_slide']))

def go_to_slide(slide):
    return __execute__(COMMANDS[COMMANDS_VERSION]['go_to_slide'] % slide)

def next_build():
    return __execute__(COMMANDS[COMMANDS_VERSION]['next_build'])

def pause_slide_show():
    return __execute__(COMMANDS[COMMANDS_VERSION]['pause_slide_show'])

def previous_build():
    return __execute__(COMMANDS[COMMANDS_VERSION]['previous_build'])

def resume_slide_show():
    return __execute__(COMMANDS[COMMANDS_VERSION]['resume_slide_show'])

def slide_show_is_playing():
    return __execute__(COMMANDS[COMMANDS_VERSION]['slide_show_is_playing'])

def slide_show_path():
    return __execute__(COMMANDS[COMMANDS_VERSION]['slide_show_path'])

def start_slide_show():
    return __execute__(COMMANDS[COMMANDS_VERSION]['start_slide_show'])

def __execute__(command):
    return __execute_with_app__(INSTALLED_VERSIONS[APPLICATION_VERSION], command)

def __execute_with_app__(app, command):
    ''' Gets provided app to execute the given applescript command '''
    to_run = 'tell application "%s" to %s' % (app, command)

    return check_output(["osascript", "-e", to_run]).strip()

def __check_output__(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    (Pinched from Python2.7 source tree)

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd)
    return output

def __scan_for_apps__():
    ''' Looks for installations of Keynote, so that we can offer an interface
    to the multiple versions of Keynote on the machine ''' 
    def walk_selective(dir, found):
        if not os.path.isdir(dir):
            return

        files = os.listdir(dir)

        for f in files:
            ff = os.path.join(dir, f)
            if f.endswith("Keynote.app"):
                found.append(ff)
            elif f.endswith(".app"):
                pass
            else:
                walk_selective(ff, found)
        return found
    candidates = walk_selective("/Applications", [])

    keynotes = {}

    for candidate in candidates:
        ver = __execute_with_app__(candidate, "version")
        keynotes[ver] = candidate

    return keynotes

def __version_tuple__(version):
    return tuple(int(i) for i in str(version).split("."))


if "check_output" not in dir(subprocess):
    check_output = __check_output__
else:
    check_output = subprocess.check_output

INSTALLED_VERSIONS = __scan_for_apps__()

select_version()
