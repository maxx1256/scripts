@echo off

call _backup_do.bat sync.007.log sync.008.log
call _backup_do.bat sync.006.log sync.007.log
call _backup_do.bat sync.005.log sync.006.log
call _backup_do.bat sync.004.log sync.005.log
call _backup_do.bat sync.003.log sync.004.log
call _backup_do.bat sync.002.log sync.003.log
call _backup_do.bat sync.001.log sync.002.log
call _backup_do.bat sync.log     sync.001.log

call d:\_sync.bat
call e:\_sync.bat

if '%COMPUTERNAME%'=='FLEXO' xcopy * D:\pub\sync_settings\ /EXCLUDE:_exclude.txt 

