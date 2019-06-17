class _const:

    
    class ConstError(TypeError): pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError
        raise NameError(name)

import sys

top = _const()

top.Config = _const()
top.Config.FileName       = "./config.ini"
top.Config.ListFileName   = "files.list"
top.Config.LogFileName    = 'musicbatch.log'

top.State = _const()
top.State.FileName        = 'state.ini'
top.State.Common          = 'common'
top.State.ListCount       = 'list_count'
top.State.LoadIndex       = 'load_index'

sys.modules[__name__] = top
