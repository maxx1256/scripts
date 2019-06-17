import configparser
import os.path
import const
import datetime
import logging
import sys


from config import *

DATETIME_MASK = "%Y-%m-%d %H:%M:%S"

class State(object):
    
    def __ReadString(self, section, name):
        if self.__config.has_option(section, name):
            return self.__config.get(section,name)
        else:
            return '';

    def __ReadInt(self, section, name):
        if self.__config.has_option(section, name):
            return self.__config.getint(section,name)
        else:
            return 0;

    def __ReadBool(self, section, name):
        if self.__config.has_option(section, name):
            return self.__config.getboolean(section,name)
        else:
            return False;

    def __ReadTime(self, section, name):
        if self.__config.has_option(section, name):
            try:
                return datetime.datetime.strptime(self.__config.get(section,name), DATETIME_MASK)
            except:
                return datetime.datetime.min
        else:
            return datetime.datetime.min

    def __WriteString(self, section, name, value):
        self.__config.set(section,name,value)
            
    def __WriteBool(self, section, name, value):
        self.__config.set(section,name,"{0}".format(value))
            
    def __WriteInt(self, section, name, value):
        self.__config.set(section,name,"{0}".format(value))

    def __WriteTime(self, section, name, value):
        self.__config.set(section, name, value.strftime(DATETIME_MASK))

            
    def Load(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
            
        self.__path = os.path.join(path, const.State.FileName)
        self.__config = configparser.ConfigParser()

        if not os.path.exists(self.__path):
            f = open(self.__path, 'w', encoding='utf-8')
            f.write('\n')
            f.close()

        self.__config.read(self.__path, encoding='utf-8')

        if not self.__config.has_section(const.State.Common):
            self.__config[const.State.Common] = {}

        self.Step            = self.__ReadString(const.State.Common, const.State.Step)
        self.RefreshList     = self.__ReadBool  (const.State.Common, const.State.RefreshList)
        self.QuickStart      = self.__ReadInt   (const.State.Common, const.State.QuickStart)
        self.ShowBuffer      = self.__ReadInt   (const.State.Common, const.State.ShowBuffer)
        self.LoadBuffer      = self.__ReadInt   (const.State.Common, const.State.LoadBuffer)
        self.ListCount       = self.__ReadInt   (const.State.Common, const.State.ListCount)
        self.LoadIndex       = self.__ReadInt   (const.State.Common, const.State.LoadIndex)
        self.FilesPerBuffer  = self.__ReadInt   (const.State.Common, const.State.FilesPerBuffer)
        self.LoadTime        = self.__ReadTime  (const.State.Common, const.State.LoadTime)
        self.ShowStartTime   = self.__ReadTime  (const.State.Common, const.State.ShowStartTime)
        self.ShowSwitchTime  = self.__ReadTime  (const.State.Common, const.State.ShowSwitchTime)

    def Save(self):
        self.__WriteString(const.State.Common, const.State.Step           , self.Step); 
        self.__WriteBool  (const.State.Common, const.State.RefreshList    , self.RefreshList);
        self.__WriteInt   (const.State.Common, const.State.QuickStart     , self.QuickStart);
        self.__WriteInt   (const.State.Common, const.State.ShowBuffer     , self.ShowBuffer); 
        self.__WriteInt   (const.State.Common, const.State.LoadBuffer     , self.LoadBuffer); 
        self.__WriteInt   (const.State.Common, const.State.ListCount      , self.ListCount); 
        self.__WriteInt   (const.State.Common, const.State.LoadIndex      , self.LoadIndex); 
        self.__WriteInt   (const.State.Common, const.State.FilesPerBuffer , self.FilesPerBuffer); 
        self.__WriteTime  (const.State.Common, const.State.LoadTime       , self.LoadTime); 
        self.__WriteTime  (const.State.Common, const.State.ShowStartTime  , self.ShowStartTime); 
        self.__WriteTime  (const.State.Common, const.State.ShowSwitchTime , self.ShowSwitchTime);
        

        with open(self.__path, 'w', encoding='utf-8') as configfile:
            self.__config.write(configfile)

        
def __test():
    conf = Config()
    state = State()
    state.Load(conf.WorkingFolder)
    print("Step = " + state.Step)
    
if __name__ == '__main__':
    __test()
        
