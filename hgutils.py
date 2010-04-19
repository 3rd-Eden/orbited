from mercurial import commands
from mercurial import hg
from mercurial import ui

class HgUtil(object):
    
    def __init__(self, repository_path):
        self._ui = ui.ui()
        self._repo = hg.repository(self._ui, repository_path)
    
    @property
    def revision(self):
        return str(self._repo[None].parents()[0])
    
    def revert(self, *files):
        # commands.revert seems to expect a date in the opts when it is called
        # we'll give it a none for that, but just so that we don't get a type
        # error
        opts = dict(date=None)
        if not files:
            opts['all'] = True
        commands.revert(self._ui, self._repo, *files, **opts)
