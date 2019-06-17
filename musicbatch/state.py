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
            return self.__config.get(section, name)
        else:
            return '';

    def __ReadInt(self, section, name):
        if self.__config.has_option(section, name):
            return self.__config.getint(section, name)
        else:
            return 0;

    def __ReadBool(self, section, name):
        if self.__config.has_option(section, name):
            return self.__config.getboolean(section, name)
        else:
            return False;

    def __ReadTime(self, section, name):
        if self.__config.has_option(section, name):
            try:
                return datetime.datetime.strptime(self.__config.get(section, name), DATETIME_MASK)
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

            
    def __init__(self):
        self.ListCount = 0
        self.LoadIndex = 0
        
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

        self.ListCount       = self.__ReadInt   (const.State.Common, const.State.ListCount)
        self.LoadIndex       = self.__ReadInt   (const.State.Common, const.State.LoadIndex)

    def Save(self):
        self.__WriteInt   (const.State.Common, const.State.ListCount      , self.ListCount); 
        self.__WriteInt   (const.State.Common, const.State.LoadIndex      , self.LoadIndex); 

        with open(self.__path, 'w', encoding='utf-8') as configfile:
            self.__config.write(configfile)

        
def __test():
    conf = Config(None)
    state = State()
    state.Load(conf.WorkingFolder)
    print("ListCount = " + "{0}".format(state.ListCount))
    
if __name__ == '__main__':
    __test()
        
