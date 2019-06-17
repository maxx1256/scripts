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
top.Config.BufferTemplate = "buffer{0}"
top.Config.ListFileName   = "files.list"
top.Config.LogFileName    = 'slideshow.log'

top.State = _const()
top.State.FileName        = 'state.ini'
top.State.Common          = 'common'
top.State.Step            = 'step'
top.State.Step_ReadList   = 'read_list'
top.State.Step_CopyFiles  = 'copy_files'
top.State.Step_StartShow  = 'start_show'
top.State.ShowBuffer      = 'show_buffer'
top.State.LoadBuffer      = 'load_buffer'
top.State.ListCount       = 'list_count'
top.State.LoadIndex       = 'load_index'
top.State.FilesPerBuffer  = 'files_per_buffer'
top.State.LoadTime        = 'load_time'
top.State.RefreshList     = 'refresh_list'
top.State.ShowStartTime   = 'show_start_time'
top.State.ShowSwitchTime  = 'show_switch_time'
top.State.QuickStart      = 'quick_start'


sys.modules[__name__] = top
