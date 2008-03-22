import rel
rel.override()

from orbited.app import Application
from orbited.config import map as config
from orbited.config import load as load_config
from orbited import __version__
import sys

from optparse import OptionParser

def load_configuration(config_file=None):
    if config_file:
        load_config(config_file)
    else:
        config_file = "(built-in)"
    print "Configuration:", config_file
        
def main():
    parser = OptionParser("usage: orbited [-d] [-c FILE]")
    parser.add_option("-c", "--config", metavar="FILE", dest="config",
                        help="write output to FILE")
    parser.add_option("-d", "--daemonize", dest="daemonize",
                        action="store_true", help="run as a daemon")
    options, args = parser.parse_args()
    
    if options.daemonize:
        daemonize(True)
    
    print "=" * 60
    print ("Orbited " + __version__).center(60)
    print "-" * 60
    load_configuration(options.config)
    print ""


    app = Application(config)
    app.start()
    
def profile():
    import hotshot
    prof = hotshot.Profile("orbited.profile")
    prof.runcall(main)
    prof.close()

def daemon():
    sys.argv.append("-d")
    main()
    
def daemonize(debug=False):
    # Copyright 2007 Jerry Seutter yello (*a*t*) thegeeks.net

    import fcntl
    import os
    import sys
    import time
    
    logger = None
    std_pipes_to_logger = True
    # Used docs by Levent Karakas 
    # http://www.enderunix.org/documents/eng/daemon.php
    # as a reference for this section.

    # Fork, creating a new process for the child.
    process_id = os.fork()
    if process_id < 0:
        # Fork error.  Exit badly.
        sys.exit(1)
    elif process_id != 0:
        # This is the parent process.  Exit.
        sys.exit(0)
    # This is the child process.  Continue.

    # Stop listening for signals that the parent process receives.
    # This is done by getting a new process id.
    # setpgrp() is an alternative to setsid().
    # setsid puts the process in a new parent group and detaches its
    # controlling terminal.
    process_id = os.setsid()
    if process_id == -1:
        # Uh oh, there was a problem.
        sys.exit(1)

    # Close file descriptors
    devnull = '/dev/null'
    if hasattr(os, "devnull"):
        # Python has set os.devnull on this system, use it instead 
        # as it might be different than /dev/null.
        devnull = os.devnull
    null_descriptor = open(devnull, 'rw')
    if not debug:
        for descriptor in (sys.stdin, sys.stdout, sys.stderr):
            descriptor.close()
            descriptor = null_descriptor

    # Set umask to default to safe file permissions when running
    # as a root daemon. 027 is an octal number.
    os.umask(027)

    # Change to a known directory.  If this isn't done, starting
    # a daemon in a subdirectory that needs to be deleted results
    # in "directory busy" errors.
    # On some systems, running with chdir("/") is not allowed,
    # so this should be settable by the user of this library.
    os.chdir('/')

    # Create a lockfile so that only one instance of this daemon
    # is running at any time.  Again, this should be user settable.
    lockfile = open('/tmp/daemonize.lock', 'w')
    # Try to get an exclusive lock on the file.  This will fail
    # if another process has the file locked.
    fcntl.lockf(lockfile, fcntl.LOCK_EX|fcntl.LOCK_NB)

    # Record the process id to the lockfile.  This is standard
    # practice for daemons.
    lockfile.write('%s' %(os.getpid()))
    lockfile.flush()

    # Logging.  Current thoughts are:
    # 1. Attempt to use the Python logger (this won't work Python < 2.3)
    # 2. Offer the ability to log to syslog
    # 3. If logging fails, log stdout & stderr to a file
    # 4. If logging to file fails, log stdout & stderr to stdout.
