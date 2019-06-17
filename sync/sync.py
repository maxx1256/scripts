# coding=utf-8

import sys
import os
import os.path
import shutil
import logging
import time

from filelist import *
from unicodefile import *

#---------------- CONFIG ---------------------

VERSION = "1.0.4"
LOG_LEVEL = logging.INFO
#LOG_LEVEL = logging.DEBUG

#--------------------------------------------


TAB = u"\t"
EOL = u"\n"

testmode = False
transferBytes = 0
transferTime  = 0.0
exclusions = list()
stdexclusions = list()

def GetLocationsFileName():
    return u"_locations"

def GetCacheFolderName():
    return u"_cache"
    
def GetChangedFolderName():
    return u"_sync_changed_"
    
def GetDeletedFolderName():
    return u"_sync_deleted_"
    
def GetLocationListName(location):
    return location + u".list"

def GetLocationExclusionName(location):
    return location + u".exclude"

def GetCacheListName():
    return u"_cache.list"
    
def GetDeletedListName():
    return u"_deleted.list"
    

def ReadLocation(name):
    location = u""
    if not os.path.exists(GetLocationsFileName()):
        return location

    fr = FileReader()
    fr.Open(GetLocationsFileName())
    while fr.Read():
        line = fr.NextLine()
        tokens = line.split(TAB, 1)
        if (tokens[0].lower() == name.lower()):
            location = os.path.normpath(tokens[1])
            break;
    fr.Close()
    return location    


def AddLocation(name, folder):
    if ReadLocation(name) != u"":
        print u"Location " + name + u" already exists"
        logging.error(u"Location " + name + u" already exists")
        return

    fw = FileWriter(GetLocationsFileName())
    fw.Append()
    s = name + TAB + folder + EOL
    fw.Write(s)
    fw.Close()
    
    
    
def LoadExclusions(location):
    global exclusions    
    global stdexclusions    
    fname = GetLocationExclusionName(location)
    if os.path.exists(fname):
        fr = FileReader()
        fr.Open(fname)
        while fr.Read():
            line = fr.NextLine().rstrip().replace("\\","/")
            if len(line) > 0:
                if line[-1] != "/":
                    line = line + "/";
                exclusions.append(line)
                logging.debug(u"custom exclusions " + line)
        fr.Close()
    stdexclusions.append(GetChangedFolderName() + "/")
    stdexclusions.append(GetDeletedFolderName() + "/")
        
#def ExcludeFoldersXXX(path):
#    global exclusions    
#    result = set()
#    for folder in exclusions:
#        s = os.path.join(path, folder)
#        result.add(s) 
#        logging.error(u"-- excluding " + s)
#    return result
#
#def ExcludeFoldersYYY(path):
#    return set([os.path.join(path, GetChangedFolderName()), os.path.join(path, GetDeletedFolderName())  ])


def InitData(location):
    path = ReadLocation(location)
    if path=="":
        logging.error(u"Invalid location " + location)
        return
    fname = GetLocationListName(location)
    f = FileList(exclusions, stdexclusions)
    f.LoadFolder(path)
    f.WriteToFile(fname)

    if not os.path.exists(GetCacheListName()):
        f.WriteToFile(GetCacheListName())
        
    if not os.path.exists(GetCacheFolderName()):
        os.mkdir(GetCacheFolderName())

def VerifyFolder(dest):
    try:
        destdir = os.path.dirname(dest)
        if not os.path.isdir(destdir):
            if testmode:
                logging.warning("Making folder " + destdir)
            else:
                logging.info(u"Making folder " + destdir)
                os.makedirs(destdir)
    except IOError as (errno, strerror):
        logging.error(u"I/O error({0}): {1}, making folder {2}".format(errno, strerror, destdir))
    
    
def Copy(src, dest):
    global transferBytes
    global transferTime

    VerifyFolder(dest)    
    try:
        if testmode:
            logging.warning("Copying file " + src + " to " + dest)
        else:
            size = os.path.getsize(src)
            start = time.clock()
            shutil.copy2(src, dest)
            len = time.clock() - start
            transferBytes += size
            transferTime  += len
    except IOError as (errno, strerror):
        logging.error(u"I/O error({0}): {1}, copying file {2}".format(errno, strerror, src))
    
def Move(src, dest):
    VerifyFolder(dest)    
    try:
        if testmode:
            logging.warning("Moving file " + src + " to " + dest)
        else:
            if os.path.exists(dest):
                os.remove(dest)
            shutil.move(src, dest)
    except IOError as (errno, strerror):
        logging.error(u"I/O error({0}): {1}, moving file {2}".format(errno, strerror, src))
    except OSError as (errno, strerror):
        logging.error(u"OS error({0}): {1}, moving file {2}".format(errno, strerror, src))
    
def CopyFile(path, fname, tolocal):
    cachefile = os.path.join(GetCacheFolderName(), fname);
    localfile = os.path.join(path, fname);
    if tolocal:
        if not os.path.exists(cachefile):
            logging.warning("Cache file is missing - " + cachefile)
            return
        if os.path.exists(localfile):
            backupfile = os.path.join(path, GetChangedFolderName(), fname)
            Move(localfile, backupfile)
        logging.info(u"Copying file " + fname + u" to local")
        Copy(cachefile, localfile)
    else:
        logging.info(u"Copying file " + fname + u" to cache")
        Copy(localfile, cachefile)
    return;    

def DeleteFile(path, fname):
    localfile = os.path.join(path, fname);
    backupfile = os.path.join(path, GetDeletedFolderName(), fname)
    logging.info(u"Deleting file " + localfile)
    Move(localfile, backupfile)
    # delete empty folder
#    localdir = os.path.dirname(localfile)
#    if os.path.getsize(localdir)==0:
#        try:
#            os.rmdir(localdir)
#        except IOError as (errno, strerror):
#            logging.error(u"I/O error({0}): {1}, removing folder {2}".format(errno, strerror, localdir))
#    

def SyncData(location):
    path = ReadLocation(location)
    if path=="":
        logging.error(u"Invalid location " + location)
        return
    
    logging.info(u"\n\nSyncing location " + location + "\n\n")
    LoadExclusions(location)
    
    # changes to apply
    listDelLocal = FileList([], stdexclusions)
    listDelCache = FileList([], stdexclusions)
    listAddCache = FileList([], stdexclusions)
    listAddLocal = FileList([], stdexclusions)
    
    # sources
    listold      = FileList([], stdexclusions)
    listcurrent  = FileList([], stdexclusions)
    listdeleted  = FileList([], stdexclusions)
    listcache    = FileList(exclusions, stdexclusions)

    if not os.path.exists(GetLocationListName(location)):
        InitData(location)

    print u"Reading..."
    
    listold.LoadFromFile(GetLocationListName(location))
    
    listcurrent.LoadFolder(path)

    if os.path.exists(GetDeletedListName()):
        listdeleted.LoadFromFile(GetDeletedListName())

    listcache.LoadFromFile(GetCacheListName())

    print u"Analyzing..."

    ''' check for added/updated '''
    entrycurrent = listcurrent.GetNext()
    entrycache   = listcache.GetNext()
    while entrycurrent != None or entrycache != None:
        loc_updated = entrycurrent!=None and entrycache!=None and entrycurrent[0]==entrycache[0] and entrycurrent[1]>entrycache[1]
        loc_added   = entrycurrent!=None and (entrycache==None or entrycurrent[0]<entrycache[0])
        rem_updated = entrycurrent!=None and entrycache!=None and entrycurrent[0]==entrycache[0]  and entrycurrent[1]<entrycache[1]
        rem_added   = entrycache  !=None and (entrycurrent==None or entrycache[0]<entrycurrent[0])

        if loc_updated or loc_added:
            listAddCache.AddEntry(entrycurrent[0], entrycurrent[1])
            
        if rem_updated or rem_added:
            listAddLocal.AddEntry(entrycache[0], entrycache[1])
    
        if loc_added:
            entrycurrent = listcurrent.GetNext()
        elif rem_added:
            entrycache   = listcache.GetNext()
        else:
            entrycurrent = listcurrent.GetNext()
            entrycache   = listcache.GetNext()
    
    ''' check for local deleted '''
    listcurrent.ResetCounter()
    entrycurrent = listcurrent.GetNext()
    entryold     = listold.GetNext()
    while entrycurrent != None or entryold != None:
        loc_deleted = entryold!=None and (entrycurrent==None or entrycurrent[0]>entryold[0])     
    
        if loc_deleted:
            listDelLocal.AddEntry(entryold[0], entryold[1])
            entryold     = listold.GetNext()
        elif entryold!=None and entrycurrent!=None and entrycurrent[0]==entryold[0]:
            entryold     = listold.GetNext()
            entrycurrent = listcurrent.GetNext()
        else:
            entrycurrent = listcurrent.GetNext()

    ''' check for remote deleted '''
    listcurrent.ResetCounter()
    entrycurrent = listcurrent.GetNext()
    entrydeleted = listdeleted.GetNext()
    while entrycurrent != None or entrydeleted != None:
        rem_deleted = entrydeleted!=None and entrycurrent!=None and entrydeleted[0]==entrycurrent[0]
        
        if rem_deleted:
            listDelCache.AddEntry(entrycurrent[0], entrycurrent[1])
            entrycurrent = listcurrent.GetNext()
            entrydeleted = listdeleted.GetNext()
        elif entrycurrent!=None and (entrydeleted==None or entrycurrent[0]<entrydeleted[0]):
            entrycurrent = listcurrent.GetNext()
        else: 
            entrydeleted = listdeleted.GetNext()

    ''' If a file was deleted locally, it will look both locally deleted and remotely added, resolve this problem '''
    entrydeleted = listDelLocal.GetNext()
    entryadded   = listAddLocal.GetNext()
    while entrydeleted != None and entryadded != None:
        if entryadded[0] < entrydeleted[0]:
            entryadded   = listAddLocal.GetNext()
        elif entryadded[0] > entrydeleted[0]:
            entrydeleted = listDelLocal.GetNext()
        else:
            if entryadded[1] > entrydeleted[1]:
                listDelLocal.RemoveCurrentEntry()
            else:
                listAddLocal.RemoveCurrentEntry()
            entrydeleted = listDelLocal.GetNext()
            entryadded   = listAddLocal.GetNext()
    
    listDelLocal.ResetCounter()
    listAddLocal.ResetCounter()

    print u"Applying changes..."

    ''' Apply the changes '''
    while listAddLocal.HasMore():
        entry = listAddLocal.GetNext()
        CopyFile(path, entry[0], True)
        
    while listAddCache.HasMore():
        entry = listAddCache.GetNext() 
        CopyFile(path, entry[0], False)

    while listDelLocal.HasMore():
        entry = listDelLocal.GetNext()
        listdeleted.AddEntry(entry[0], entry[1])
        
    while listDelCache.HasMore():
        entry = listDelCache.GetNext()
        DeleteFile(path, entry[0])
        

    if not testmode:
        ''' write new file of deleted files '''
        if listDelLocal.Count()>0:
            listdeleted.WriteToFile(GetDeletedListName())
        ''' new cache file is current local state because we copied all the changes '''
        print u"Rereading..."
        listcurrent.LoadFolder(path)
        listcurrent.WriteToFile2(GetCacheListName(), listcache.GetExcludedFiles())
        listcurrent.WriteToFile(GetLocationListName(location))

    speed = 0.0
    if transferTime > 0.0001:
        speed = transferBytes/transferTime/1024/1024
    
    logging.info(u"Copied {0:,} bytes in {1:.2f} seconds".format(transferBytes,transferTime)) 
    logging.info(u"Sync completed! Average speed {0:.2f} MB/sec.".format(speed) )

    



def CheckArgv(minrequired, message):
    if len(sys.argv) < minrequired:
        print(message)
        sys.exit()

def main():
    global testmode
    
    logging.basicConfig(filename='sync.log', format='%(asctime)s %(levelname)s : %(message)s', level=LOG_LEVEL)
    
#    AddLocation(u"bob", u"c:\\temp\\1");
#    SyncData(u"1")
    #return
    
    print "sync ver. " + VERSION + "\n"
    CheckArgv( 2, "Usage sync <add>|<sync>|<testsync>")
        
    if sys.argv[1] == "add":
        CheckArgv( 4, "Adds new location and path to it.\n Usage: sync add location_name location_path")
        AddLocation(unicode(sys.argv[2]), unicode(sys.argv[3]));
    
    elif sys.argv[1] == "sync":
        CheckArgv( 3, "Synchronizes the data.\n Usage: sync sync location_name")
        testmode = False
        SyncData(unicode(sys.argv[2]));
    
    elif sys.argv[1] == "testsync":
        CheckArgv( 3, "Test Synchronizing the data.\n Usage: sync testsync location_name")
        testmode = True
        SyncData(unicode(sys.argv[2]));
    

if __name__ == '__main__':
    main()
    
    