#!/usr/bin/env python
from optparse import OptionParser
import os
import subprocess
import sys

from hgutils import HgUtil

PYTHON = sys.executable
SETUP_PY = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        'daemon', 'setup.py')
                                        
def shell(command, working_directory=None):
    cwd = working_directory or os.getcwd()
    print cwd, command
    returncode = subprocess.call(command, shell=True, cwd=cwd)
    return returncode

class SetupCfg(object):
    """ A context manager that will restore the local repository when it exits
    
        When SetupCfg is created it takes a list of 3-tuples that look like:
          (<setup.cfg section>, <option name>, <new value>)
        
        When the context is exited, an hg revert is applied to the local
        repository so that any changes made are erased.
    """
    
    def __init__(self, configuration_options):
        self._options = configuration_options
        self._hg = HgUtil('.')
        self._setup_cfg_exists = os.path.exists('daemon/setup.cfg')

    def __enter__(self):
        for application, option, value in self._options:
            self._set_option(application, option, value)
       
    def __exit__(self, *args, **kwargs):
        if self._setup_cfg_exists:
            self._hg.revert('daemon/setup.cfg')
        else:
            os.remove('daemon/setup.cfg')
        # return False; we never have a reason to suppress an exception
        return False
    
    @staticmethod
    def _set_option(app, opt, value):
        setopt = ' '.join([PYTHON, SETUP_PY, 'setopt',
                           '--command', app,
                           '--option', opt,
                           '--set-value', value])
        return shell(setopt)
        
class ReleaseManager(object):
    
    def __init__(self, repository_path):
        self._path = repository_path
        self._hg = HgUtil(self._path)
    
    def make_release(self, type, upload=True):
        command = [PYTHON, 'setup.py', type]
        if upload:
            command.append('upload')
        script_dir = os.path.abspath(os.path.dirname(__file__))
        daemon_dir = os.path.join(script_dir, 'daemon')
        command_string = " ".join(command)
        shell(command_string, working_directory=daemon_dir)
    
    def snapshot(self, type='sdist'):
        repo = HgUtil('.')
        revision = repo.revision
        dev_tag = '-dev-%(revision)s' % dict(revision=revision)
        with SetupCfg([('egg_info', 'tag_build', dev_tag)]):
            self.make_release(type)

def make_parser():
    parser = OptionParser()
    return parser

def main(argv):
    parser = make_parser()
    (options, args) = parser.parse_args(argv)
    script = args.pop(0)
    release_type = args[0]
    
    releaser = ReleaseManager('.')
    releaser.snapshot(release_type)

if (__name__=='__main__'):
    main(sys.argv)
