import logging
import os.path
import shutil
from filelist import *

MetadataFolder = u"_sync_metadata_"
MetadataIdFile = u"location_id"
TAB = u"\t"
EOL = u"\n"


def GetLocationsFileName():
    return u"_locations"

def GetLocationListName(location):
    return os.path.join(ReadLocation(location), MetadataFolder, location + u".list")

def __GetLocationListNameOld(location):
    return location + u".list"

def GetLocationExclusionName(location):
    return os.path.join(ReadLocation(location), MetadataFolder, location + u".exclude")

def __GetLocationExclusionNameOld(location):
    return location + u".exclude"

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

    if not __ValidateLocationIdFile(name, folder):
        __AddLocationIdFile(name, folder)

    # add to the location list
    fw = FileWriter(GetLocationsFileName())
    fw.Append()
    s = name + TAB + folder + EOL
    fw.Write(s)
    fw.Close()


def UpgradeLocation(name):
    # copy file list first
    newFileName = GetLocationListName(name)
    oldFileName = __GetLocationListNameOld(name)
    if (not os.path.exists(newFileName)) and os.path.exists(oldFileName):
        destdir = os.path.dirname(newFileName)
        print u"Moving file list to new location " + destdir
        logging.info(u"Moving file list to new location " + destdir)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        shutil.move(oldFileName, newFileName)

    # copy exclusions
    newFileName = GetLocationExclusionName(name)
    oldFileName = __GetLocationExclusionNameOld(name)
    if (not os.path.exists(newFileName)) and os.path.exists(oldFileName):
        destdir = os.path.dirname(newFileName)
        print u"Moving exclusion list to new location " + destdir
        logging.info(u"Moving exclusion list to new location " + destdir)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        shutil.move(oldFileName, newFileName)

    # create id file last
    folder = ReadLocation(name)
    if not __ValidateLocationIdFile(name, folder):
        __AddLocationIdFile(name, folder)

def __ValidateLocationIdFile(name, folder):
    # id file exists and contains correct name
    path = os.path.join(folder, MetadataFolder, MetadataIdFile)
    if not os.path.exists(path):
        return False

    fr = FileReader()
    fr.Open(path)
    if fr.Read():
        line = fr.NextLine()
        if (line.lower() == name.lower()):
            return True
        else:
            raise RuntimeError(u"Folder " + folder + u" is already registered as location " + line)
    return False

def __AddLocationIdFile(name, folder):
    # write id to the location metadata
    metadataFolder = os.path.join(folder, MetadataFolder)
    if not os.path.exists(metadataFolder):
        os.makedirs(metadataFolder)

    metadataPath = os.path.join(metadataFolder, MetadataIdFile)
    if os.path.exists(metadataPath):
        print u"Folder " + folder + u" already contains metadata"
        logging.error(u"Folder " + folder + u" already contains metadata")
        return

    destFile = os.path.join(folder, MetadataFolder, MetadataIdFile)
    print u"Creating id file " + destFile
    logging.info(u"Creating id file " + destFile)

    idWriter = FileWriter(destFile)
    idWriter.Overwrite();
    idWriter.Write(name + EOL)
    idWriter.Close()


if __name__ == '__main__':
    #AddLocation("c", "d:\\test\\c")
    #print(ReadLocation("a"))
    #print (__ValidateLocation("c", "d:\\test\\c"))
    UpgradeLocation("b")
