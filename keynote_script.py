#!/usr/bin/env python2.6

import pipes
import subprocess

def export_slide_show(to_directory):
	''' Outputs a KPF at to_directory '''
	command = 'export front slideshow to "%s" as KPF_RAW' % (pipes.quote(to_directory))
	return __execute__(command)

def get_current_slide():
	return int(__execute__("slide number of current slide of front slideshow").strip())

def go_to_slide(slide):
	return __execute__("jump to slide %d of front slideshow" % slide)

def next_build():
	return __execute__("show next")

def previous_build():
	return __execute__("show previous")

def start_slide_show():
	return __execute__("start")

def __execute__(command):
	''' Gets keynote to execute the given applescript command '''
	to_run = 'tell application "Keynote" to %s' % command

	return check_output(["osascript", "-e", to_run])


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

if "check_output" not in dir(subprocess):
	check_output = __check_output__
else:
	check_output = subprocess.check_output