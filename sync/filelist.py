# coding=utf-8

import sys
import os
import os.path
import logging

from unicodefile import *

DELIMITER = u"*"

class FileList(object):

    def __init__(self, exclusions, stdexclusions):
        self.__files = []
        self.__excludedfiles = []
        self.__path = ""
        self.__pathlen = 0
        self.__next = 0
        self.__exclusions = exclusions
        self.__stdexclusions = stdexclusions
        os.stat_float_times(False)

        
    def Error(self, msg):
        logging.error(msg)
        print msg
        sys.exit(1)
        

    def __DoLoadFolder(self, path):
        logging.debug("Reading folder " + path)
        files = os.listdir(path)
        filecount = 0
        for fname in files:
            logging.debug("Found file "+fname)
            fullfname = os.path.join(path, fname.rstrip())
            if os.path.isdir(fullfname):
                subcount = self.__DoLoadFolder(fullfname)
                filecount = filecount + subcount
                if subcount==0:
                    try:
                        logging.info("Deleting empty folder " + fullfname)
                        os.rmdir(fullfname)
                    except:
                        logging.error("Error deleting empty folder " + fullfname)
            else:
                try:
                    filecount = filecount+1
                    ftime = long(os.path.getmtime(fullfname))
                    fsize = long(os.path.getsize(fullfname))
                    self.AddEntry(fullfname[self.__pathlen:], ftime, fsize)
                except:
                    #print "*** File " + fullfname + " is no good, skipping"
                    logging.error("*** File " + fullfname + " is no good, skipping")
        return filecount

        
    def LoadFolder(self, path):
        logging.debug(u"Loading FileList from folder: " + path)
        if not os.path.exists(path):
            self.Error(u"Path " + path + u" does not exist")
        self.__path = path
        self.__pathlen = len(path)+1
        self.__files = []
        self.__excludedfiles = []
        self.__DoLoadFolder(self.__path)
        self.__Sort()
          

    def WriteToFile(self, fname):
        fw = FileWriter(fname)
        fw.Overwrite()
        for x in self.__files:
            fw.Write(u"{0}{1}{2}{3}{4}\n".format(x[0], DELIMITER, x[1], DELIMITER, x[2]))
        fw.Close()
        
    def WriteToFile2(self, fname, extraentries):
        fw = FileWriter(fname)
        fw.Overwrite()
        for x in self.__files:
            fw.Write(u"{0}{1}{2}{3}{4}\n".format(x[0], DELIMITER, x[1], DELIMITER, x[2]))
        for x in extraentries:
            fw.Write(u"{0}{1}{2}{3}{4}\n".format(x[0], DELIMITER, x[1], DELIMITER, x[2]))
        fw.Close()
        

    def LoadFromFile(self, fname):
        logging.debug(u"Loading FileList from file: " + fname)
        self.__files = []
        self.__excludedfiles = []
        fr = FileReader()
        fr.Open(fname)
        while fr.Read():
            line = fr.NextLine()
            tokens = line.split(DELIMITER, 2)
            self.AddEntry(tokens[0], tokens[1], tokens[2])
        fr.Close()
        self.__Sort()
        

    def __Sort(self):
        self.__files.sort(key=lambda entry: entry[0])
        self.__next = 0
        
        
    def HasMore(self):
        return self.__next < len(self.__files)
    
    
    def GetNext(self):
        if self.__next < len(self.__files):
            idx = self.__next
            self.__next = self.__next+1  
            return self.__files[idx]
        else:
            return None
        
    def ResetCounter(self):    
        self.__next = 0
        
        
    def AddEntry(self, fname, ftime, fsize):
        fname = fname.replace("\\", "/")
        for excl in self.__exclusions:
            if fname.startswith(excl):
                entry = (fname, long(ftime), long(fsize))
                self.__excludedfiles.append(entry)
                logging.debug(u"Skipping entry in excluded folder: " + fname)
                return
        for excl in self.__stdexclusions:
            if fname.startswith(excl):
                logging.debug(u"Skipping entry in excluded folder: " + fname)
                return
        logging.debug(u"Adding entry: " + fname)
        entry = (fname, long(ftime), long(fsize))
        self.__files.append(entry)
        
    def RemoveCurrentEntry(self):
        if self.__next>0: 
            idx = self.__next-1
            self.__files.pop(idx)
            self.__next = idx
        
    def Count(self):
        return len(self.__files) 
    
    def GetExcludedFiles(self):
        return self.__excludedfiles
        
#-----------------------------------------------
    
def __test():
    logging.basicConfig(filename='sync.log', format='%(asctime)s %(levelname)s : %(message)s', level=logging.DEBUG)

    ex = list()
    stdex = list()

    ex.append("PHOTO")

    toady = FileList(ex, stdex)
    toady.AddEntry("bob", 1, 2)
    fname, ftime, fsize = toady.GetNext()
    print u'{0} {1} {2}'.format(fname, ftime, fsize)


    f = FileList(ex, stdex)
    f.LoadFolder(u"c:\\temp")
    f.WriteToFile(u"bob.list")

    print u"--- Excluded files:"
    ex = f.GetExcludedFiles()
    for x in ex:
        print u"{0}  {1} {2}".format(x[0], x[1], x[2])
        
    f.LoadFromFile(u"bob.list")
    f.WriteToFile(u"bob2.list")
    
    print u"--- Loaded files:"
    f.ResetCounter()
    while f.HasMore():
        fname, ftime, fsize = f.GetNext()
        print u"{0}  {1} {2}".format(fname, ftime, fsize )
        
if __name__ == '__main__':
    __test()
