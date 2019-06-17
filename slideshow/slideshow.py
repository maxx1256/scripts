import configparser
import os.path
import time
import logging
import socket
import sys
import random
import datetime
import signal
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure
import shutil

import const

from config import *
from state import *

VERSION = "1.0.5"

LOG_LEVEL = logging.INFO
#LOG_LEVEL = logging.DEBUG

DATETIME_MASK = "%Y-%m-%d %H:%M:%S"

class SlideShow(object):

    def __init__(self, configfile):
        self._config = Config(configfile)
        self._state = State()
        self._state.Load(self._config.WorkingFolder)
        self._viewerPID = 0

    def BufferPath(self, index):
        path = os.path.join(self._config.WorkingFolder, const.Config.BufferTemplate.format(index))
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def _Connect(self):
        client_machine_name = 'slideshow'
        
        conn = SMBConnection(self._config.RemoteUser, self._config.RemoteUserPwd, client_machine_name, self._config.RemoteServer)
        result = conn.connect(socket.gethostbyname(self._config.RemoteServer))
        if not result:
            logging.error("Failed to connect to {0}".format(self._config.RemoteServer))
            return None

        return conn

    def _AcceptFile(self, path):
        lowname = path.lower()
        if not lowname.endswith(('.png', '.jpg', '.jpeg')):
            return False
        for skip in self._config.SkipList:
            if skip in lowname:
                return False

        return True
        
                    
    def _ScanShare(self, conn, path, files):
        for f in conn.listPath(self._config.RemoteShare, path):
            if f.filename != '.' and f.filename != '..':
                if f.isDirectory:
                    self._ScanShare(conn, os.path.join(path, f.filename), files)
                else:
                    filepath = os.path.join(path, f.filename)
                    if self._AcceptFile(filepath):
                        files.append(filepath)

        
    def _ReadList(self):
        try:
            self._state.ListCount = 0
            self._state.Save()

            conn = None
            conn = self._Connect()
            if conn is None:
                return False
            logging.info("_ReadList: Connected to {0}".format(self._config.RemoteServer))

            # read list
            files = []
            self._ScanShare(conn, self._config.RemotePath, files)
            count = len(files)
            logging.info("_ReadList: Retrieved {0} file names".format(count))

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
            self._state.Save()
            return True
        except OSError as err:
            logging.error("_ReadList: OS error: {0}".format(err))
            return False
        except:
            logging.error("_ReadList: Unexpected error: {0}".format(sys.exc_info()[0]))
            raise
        finally:
            if not conn is None:
                conn.close()
                logging.info("_ReadList: Disconnected from {0}".format(self._config.RemoteServer))

    def _EmptyFolder(self, path):
        files = os.listdir(path)
        for fname in files:
            fullname = os.path.join(path, fname.rstrip())
            if os.path.isdir(fullname):
                try:
                    self._EmptyFolder(fullname)
                    os.rmdir(fullname)
                except:
                    logging.error("Error deleting folder ")
            else:
                try:
                    os.remove(fullname)
                except:
                    logging.error("Error deleting file ")

    def _CanReadFile(self, conn, path):
        try:
            attr = conn.getAttributes(self._config.RemoteShare, path)
            return True
        except OperationFailure as err:
            logging.error("_CanReadFile: unable to read fil0: {0}".format(path))
            return False
    
    def _CopyFiles(self):
        startindex = self._state.LoadIndex
        bufferfolder = self.BufferPath(self._state.LoadBuffer)
        if self._state.QuickStart != 2:
            self._EmptyFolder(bufferfolder)
            logging.info("_CopyFiles: Emptied buffer {0}".format(self._state.LoadBuffer))

        try:
            conn = None
            conn = self._Connect()
            if conn is None:
                return False

            #raise ValueError('A very specific bad thing happened')

            logging.info("_CopyFiles: Connected to {0}".format(self._config.RemoteServer))
            listname = os.path.join(self._config.WorkingFolder, const.Config.ListFileName)
            if self._state.QuickStart == 1:
                desiredcount = self._config.FilesPerBufferQuick
            elif self._state.QuickStart == 2:
                desiredcount = self._state.FilesPerBuffer - self._config.FilesPerBufferQuick
            else:
                desiredcount = self._state.FilesPerBuffer
                
            index = 0
            count = 0
            with open(listname, 'r', encoding='utf-8') as filelist:
                for filename in filelist:
                    if index >= startindex:
                        filename = filename.rstrip("\r\n")
                        destpath = os.path.join(bufferfolder, filename)
                        destdir = os.path.dirname(destpath)
                        if not os.path.isdir(destdir):
                            os.makedirs(destdir)

                        if self._CanReadFile(conn, filename):
                            with open(destpath, 'wb') as destfile:
                                conn.retrieveFile(self._config.RemoteShare, filename, destfile)
                                destfile.close()

                        count = count+1
                        if count % 50 == 0:
                            self._state.LoadIndex = index+1
                            self._state.Save()
                            print("{0} Copied {1} files to buffer {2}".format(datetime.datetime.now().strftime(DATETIME_MASK), count, self._state.LoadBuffer))

                    index = index + 1
                    if index >= startindex + desiredcount:
                        break
                filelist.close()

            logging.info("_CopyFiles: Copied {0} files positions [{1}-{2}] to buffer {3}. Load time {4}".
                         format(count, startindex, index-1, self._state.LoadBuffer, self._state.LoadTime.strftime(DATETIME_MASK)))
            print("{0} Finished copying {1} files to buffer {2}".format(datetime.datetime.now().strftime(DATETIME_MASK), count, self._state.LoadBuffer))

            self._state.LoadIndex = index
            self._state.LoadTime = datetime.datetime.now()
            self._state.Save()
            return True

        except OSError as err:
            logging.error("_CopyFiles: OS error: {0}".format(err))
            return False
        except OperationFailure as err:
            logging.error("_CopyFiles: OperationFailure: {0}".format(err))
            return False
        except:
            logging.error("_CopyFiles: Unexpected error: {0}".format(sys.exc_info()[0]))
            return False
        finally:
            if not conn is None:
                conn.close()
                logging.info("_CopyFiles: Disconnected from {0}".format(self._config.RemoteServer))

    # return true for next action, false to wait and retry
    def _TryStartShow(self):
        now = datetime.datetime.now()
        
        # it is time to switch  and we have fresh buffer loaded
        if now > self._state.ShowSwitchTime and self._state.ShowStartTime < self._state.LoadTime:
            logging.info("_TryStartShow: switching show to load buffer {0}.\n"
                         "Current time {1}, switch time {2}, show start time {3}, load time {4}".
                         format(self._state.LoadBuffer,
                                now.strftime(DATETIME_MASK),
                                self._state.ShowSwitchTime.strftime(DATETIME_MASK),
                                self._state.ShowStartTime.strftime(DATETIME_MASK),
                                self._state.LoadTime.strftime(DATETIME_MASK)))
            self._StopShow()
            self._state.ShowBuffer = self._state.LoadBuffer
            if self._state.QuickStart == 1:
                self._state.QuickStart = 2
            else:
                self._state.QuickStart = 0
                if self._state.LoadBuffer == 0:
                    self._state.LoadBuffer = 1
                else:
                    self._state.LoadBuffer = 0
                self._state.ShowSwitchTime = now.replace(hour=self._config.SwitchHour, minute=0, second=0)
                if self._state.ShowSwitchTime <= now:
                    self._state.ShowSwitchTime = self._state.ShowSwitchTime + datetime.timedelta(days=1)
                if self._state.ShowSwitchTime - now < datetime.timedelta(hours=4):
                    self._state.ShowSwitchTime = self._state.ShowSwitchTime + datetime.timedelta(days=1)

            self._state.LoadTime = datetime.datetime.min
            self._StartShow()
            self._state.ShowStartTime = now

            logging.info("_TryStartShow: started show in buffer {0}.\n"
                         "Current time {1}, switch time {2}, show start time {3}, load time {4}".
                         format(self._state.ShowBuffer,
                                now.strftime(DATETIME_MASK),
                                self._state.ShowSwitchTime.strftime(DATETIME_MASK),
                                self._state.ShowStartTime.strftime(DATETIME_MASK),
                                self._state.LoadTime.strftime(DATETIME_MASK)))
            return True
                
        self._StartShow()
        return False

    def _StartShowOnStartup(self):
        if self._state.Step == const.State.Step_CopyFiles and self._state.LoadIndex > 0:
            self._StartShow()
    
    def _StopShow(self):
        if self._viewerPID != 0:
            logging.info("_StopShow: Killing process {0}".format(self._viewerPID))
            os.kill(self._viewerPID, signal.SIGTERM)
            self._viewerPID = 0
        else:
            logging.info("_StopShow: No process to kill")
        
    def _StartShow(self):
        if self._viewerPID == 0:
            logging.info("_StartShow: starting show in buffer {0}".format(self._state.ShowBuffer))

            wait = '{0}'.format(self._config.WaitTime)
            showfolder = self.BufferPath(self._state.ShowBuffer)
            
            args = ['pqiv', '-f', '-l', '-s', '-d', wait, '--shuffle', showfolder]
            self._viewerPID = os.spawnvp(os.P_NOWAIT, 'pqiv', args) 

    def _RotateLogs(self, logfile):
        oldName = "{0}{1}".format(logfile, "6")
        for idx in ["5","4","3","2","1",""]:
            if os.path.isfile(oldName):
                os.remove(oldName)
            newName = "{0}{1}".format(logfile, idx)
            if os.path.isfile(newName):
                shutil.copy2(newName, oldName)
            oldName = newName
        
    def _InitialSetup(self):
        self._state.QuickStart = True
        self._state.ShowBuffer = 0
        self._state.LoadBuffer = 1
        self._state.ListCount  = 0
        self._state.QuickStart = 1
        self._state.LoadTime      = datetime.datetime.min
        self._state.ShowStartTime = datetime.datetime.min
        self._state.ShowSwitchTime= datetime.datetime.now()
        
        self._state.Step = const.State.Step_ReadList
        self._state.Save()
    
    def Run(self):
        logfile = os.path.join(self._config.WorkingFolder, const.Config.LogFileName)
        self._RotateLogs(logfile)
        print("log file {0}".format(logfile))
        logging.basicConfig(filename=logfile, format='%(asctime)s %(levelname)s : %(message)s', level=LOG_LEVEL, filemode='w')

        self._StartShowOnStartup()
        
        while True:
            logging.debug("Run: step {0}".format(self._state.Step))
            
            if self._state.Step == const.State.Step_ReadList:
                if self._ReadList():
                    self._state.Step = const.State.Step_CopyFiles
                    self._state.LoadIndex = 0
                    chunks = self._state.ListCount // self._config.FilesPerBuffer + 1
                    self._state.FilesPerBuffer = self._state.ListCount // chunks + 1
                    self._state.Save()
                else:
                    time.sleep(self._config.RetryDelay)
            elif self._state.Step == const.State.Step_CopyFiles:
                if self._CopyFiles():
                    self._state.RefreshList = (self._state.LoadIndex >= self._state.ListCount)
                    self._state.Step = const.State.Step_StartShow
                    self._state.Save()
                else:
                    time.sleep(self._config.RetryDelay)
            elif self._state.Step == const.State.Step_StartShow:
                if self._TryStartShow():
                    if self._state.RefreshList:
                        self._state.Step = const.State.Step_ReadList
                    else:
                        self._state.Step = const.State.Step_CopyFiles
                    self._state.Save()
                time.sleep(self._config.RetryDelay)
            else:
                self._InitialSetup()

    
def CheckArgv(minrequired, message):
    if len(sys.argv) < minrequired:
        print(message)
        sys.exit()

print ("slideshow ver. " + VERSION + "\n")
CheckArgv( 2, "Usage slideshow <configfile>")

if len(sys.argv) < 2:
    configfile = None
else:
    configfile = sys.argv[1]
show = SlideShow(configfile)
show.Run()



