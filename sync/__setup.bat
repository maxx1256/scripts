
echo trailer > d.exclude

c:\python27\python sync.py add a d:\test\a
c:\python27\python sync.py add b d:\test\b
c:\python27\python sync.py add c d:\test\c
c:\python27\python sync.py add d d:\test\d

c:\python27\python sync.py sync a
c:\python27\python sync.py sync b
c:\python27\python sync.py sync c
c:\python27\python sync.py sync d
