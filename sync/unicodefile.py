# coding=utf-8

import os

ENCODING = 'utf-8'


class FileWriter(object):
    
    ''' Creates a file if does not exist '''    
    def __init__(self, name):
        self.__name = name
        self.__f = None
        if not os.path.exists(name):
            f = file(name, 'w')
            f.write("")
            f.close()
            
    def __del__(self):
        self.Close()
        
    def Overwrite(self):
        self.__f = open(self.__name,"wb")
        self.__f.seek(os.SEEK_SET, 0)
        self.__f.truncate()
        
    def Append(self):
        self.__f = open(self.__name,"ab")

    ''' we must receive unicode on input! 
        but we store utf-8 encoded lines in the file ''' 
    def Write(self, line):
        lineascii = line.encode(ENCODING)
        self.__f.write(lineascii)
        
    def Close(self):
        if self.__f != None:
            self.__f.close()
            self.__f = None
        
        
#-----------------------------------------------------

class FileReader(object):
    

    ''' Creates a file if does not exist '''    
    def __init__(self):
        self.__f = None
        self.__nextline = u"";
            
    def __del__(self):
        self.Close()
        
    def Open(self, name):
        self.__f = open(name,"r")
        
    ''' lines in the file are utf-8 encode, but we return unicode '''    
    def Read(self):
        lineascii = self.__f.readline()
        if lineascii=="":
            return False
        self.__nextline = lineascii.rstrip("\r\n").decode(ENCODING)
        return True
        
    def NextLine(self):
        return self.__nextline
        
        
    def Close(self):
        if self.__f != None:
            self.__f.close()
            self.__f = None
        
#-----------------------------------------------------

def __test():
    fw = FileWriter("bob.txt")
    fw.Overwrite()
    fw.Write(u"Hello there Всегда вперед\n")
    fw.Write(u"Shit!\n")
    fw.Close()
    
    fr = FileReader()
    fr.Open("bob.txt")
    while fr.Read():
        print fr.NextLine()
    fr.Close()
    
    
if __name__ == '__main__':
    __test()
    
        
        