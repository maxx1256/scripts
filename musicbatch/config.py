import configparser
import const

class Config(object):
    
    def __init__(self, configfile):

        c = configparser.ConfigParser()
        if configfile is None:
            c.read(const.Config.FileName,  encoding='utf-8')
        else:
            c.read(configfile,  encoding='utf-8')
        
        self.WorkingFolder      = c.get   ('Common', 'WorkingFolder')
        self.SourceFolder       = c.get   ('Common', 'SourceFolder')
        self.DestFolder         = c.get   ('Common', 'DestFolder')
        self.DestFolderSizeMB   = c.getint('Common', 'DestFolderSizeMB')
        self.SkipList           = c.get   ('Common', 'SkipList').lower().split(',')
        self.ExtensionList      = c.get   ('Common', 'ExtensionList').lower().split(',')
        self.MaxFolderNameLen       = c.getint('Common', 'MaxFolderNameLen')

def __test():
    c = Config(None)
    print(c.WorkingFolder)
    print(c.DestFolder)
    print(c.DestFolderSizeMB)
    print(c.SkipList)
    print(c.ExtensionList)
    
if __name__ == '__main__':
    __test()
        
