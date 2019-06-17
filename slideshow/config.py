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
        self.WaitTime           = c.getint('Common', 'WaitTime')
        self.RetryDelay         = c.getint('Common', 'RetryDelay')
        self.FilesPerBuffer     = c.getint('Common', 'FilesPerBuffer')
        self.FilesPerBufferQuick= c.getint('Common', 'FilesPerBufferQuick')
        self.SwitchHour         = c.getint('Common', 'SwitchHour')
        self.SkipList           = c.get   ('Common', 'SkipList').lower().split(',')

        self.RemoteServer       = c.get('RemoteServer', 'ServerName')
        self.RemoteShare        = c.get('RemoteServer', 'Share')
        self.RemoteUser         = c.get('RemoteServer', 'UserName')
        self.RemoteUserPwd      = c.get('RemoteServer', 'UserPassword')
        self.RemotePath         = c.get('RemoteServer', 'Path')
        

        
def __test():
    c = Config(None)
    print(c.WorkingFolder)
    print(c.RetryDelay)
    print('RemoteShare: ' + c.RemoteShare)
    print('RemotePath: ' + c.RemotePath)
    
if __name__ == '__main__':
    __test()
        
