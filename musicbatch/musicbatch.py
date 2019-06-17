import os.path
import time
import random
import shutil
import sys
import datetime

import normalizer
import state
import config
import const

VERSION = "1.0.4"

DATETIME_MASK = "%Y-%m-%d %H:%M:%S"

class MusicBatch(object):

    def __init__(self, configfile):
        self._config = config.Config(configfile)
        self._state = state.State()
        self._state.Load(self._config.WorkingFolder)
        self._normalizer = normalizer.Normalizer(self._config.MaxFolderNameLen)

    def _AcceptFile(self, path):
        if not os.path.isfile(path):
            return False

        lowname = path.lower()
        ext = os.path.splitext(lowname)[1]
        if not (ext in self._config.ExtensionList):
            return False

        for skip in self._config.SkipList:
            if skip in lowname:
                return False

        return True

    def _ScanFolder(self, path, files):
        for f in os.listdir(path):
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                self._ScanFolder(fullpath, files)
            elif self._AcceptFile(fullpath):
                files.append(os.path.relpath(fullpath, self._config.SourceFolder))
        
    def _ReadList(self):
        self._state.ListCount = 0
        self._state.Save()

        # read list
        files = []
        self._ScanFolder(self._config.SourceFolder, files)
        count = len(files)
        msg = "_ReadList: Retrieved {0} file names".format(count)
        print(msg)

        # shuffle
        for i in range(count):
            n = random.randrange(count)
            if i != n:
                s = files[i]
                files[i] = files[n]
                files[n] = s

        # save list
        listname = os.path.join(self._config.WorkingFolder, const.Config.ListFileName)
        f = open(listname, 'w', encoding='utf-8')
        for line in files:
            f.write(line+'\n')
        f.close()

        self._state.ListCount = count
        self._state.LoadIndex = 0
        self._state.Save()
        print("Read list complete")

    def _EmptyFolder(self, path):
        if os.path.isdir(path):
            files = os.listdir(path)
            for fname in files:
                fullname = os.path.join(path, fname.rstrip())
                if os.path.isdir(fullname):
                    self._EmptyFolder(fullname)
                    os.rmdir(fullname)
                else:
                    os.remove(fullname)

    def _CopyFiles(self):
        print("Cleaning the old files in " + self._config.DestFolder) 
        self._EmptyFolder(self._config.DestFolder)

        print("Copying files to " + self._config.DestFolder)
        index = 0
        count = 0
        listname = os.path.join(self._config.WorkingFolder, const.Config.ListFileName)
        spaceused = 0
        batchsize = 0
        maxspaceused = self._config.DestFolderSizeMB * 1024 * 1024
        with open(listname, 'r', encoding='utf-8') as filelist:
            starttime = time.time()
            for filename in filelist:
                # skip the already copied files
                if index < self._state.LoadIndex:
                    index = index + 1
                    continue

                if index >= self._state.ListCount:
                    break

                filename = filename.rstrip("\r\n")

                lowname = filename.lower()
                for skip in self._config.SkipList:
                    if skip in lowname:
                        continue
                
                srcpath = os.path.join(self._config.SourceFolder, filename)
                destfilename = self._normalizer.normalize_path(filename)
                destpath = os.path.join(self._config.DestFolder, destfilename)

                filesize = os.path.getsize(srcpath)
                if (spaceused + filesize >= maxspaceused):
                    break

                # keep a megabite free
                total, used, free = shutil.disk_usage(self._config.DestFolder)
                if free < filesize + 1024*1024:
                    break

                try:
                    destdir = os.path.dirname(destpath)
                    if not os.path.isdir(destdir):
                        os.makedirs(destdir)
                    shutil.copy2(srcpath, destpath)
                    spaceused = spaceused + filesize
                    batchsize = batchsize + filesize

                    index = index + 1
                    count = count + 1
                except OSError as err:
                    print("_CopyFiles: OS error: {0}".format(err))
                    break
                
                if count % 50 == 0:
                    speed = batchsize / (time.time() - starttime) // 1024
                    print("{0} Copied {1} files, speed {2} kB/sec".format(datetime.datetime.now().strftime(DATETIME_MASK), count, speed))
                    starttime = time.time()
                    batchsize = 0

            filelist.close()

        print("{0} Finished copying {1} files to {2}, space used {3} MB".format(datetime.datetime.now().strftime(DATETIME_MASK), count, self._config.DestFolder, spaceused//2**20))

        self._state.LoadIndex = index
        self._state.Save()


    def Run(self):
        if self._state.ListCount == 0 or self._state.LoadIndex >= self._state.ListCount:
            self._ReadList()

        self._CopyFiles()

    
def CheckArgv(minrequired, message):
    if len(sys.argv) < minrequired:
        print(message)
        sys.exit()

print ("musicbatch ver. " + VERSION + "\n")
CheckArgv( 2, "Usage musicbatch <configfile>")

if len(sys.argv) < 2:
    configfile = None
else:
    configfile = sys.argv[1]
show = MusicBatch(configfile)
show.Run()



