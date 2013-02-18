# -*- coding: utf-8 -*-

'''
Created on 15.10.2012
main
wk_dir = root
    os.walk (root, dirs, files)
    search *.mov in files
        yes: run convert root+files[i]
            move *.mov into thrash dir saving original pathname to easy backup
                
@author: nedr
'''

if __name__ == '__main__':
    pass

import os, subprocess
from os.path import join, getsize

source_dir = '/home/nedr/progs/convert/test_area'
dest_dir = '/home/nedr/progs/convert/test_area/converted'
source_extention = '.mov'
dest_extention = '.avi'
command = 'ffmpeg'
options = ''
movnames = []   # list with filenames
# os.path.join(dirpath, name)
for dirpath, dirnames, filenames in os.walk(source_dir, topdown=True):
    for filename in filenames:
        sourcefilename = join(dirpath, filename)
        destfilename = join(dirpath, filename + dest_extention)
        if (filename.endswith(source_extention) and 
            not (os.path.exists(destfilename)
            and getsize(destfilename) != 0)):
            print sourcefilename 
            print '--> %s' %destfilename
            #subprocess.call(['echo', command, sourcefilename, destfilename,
            #                 options])
    
    """for fname in files:
        if (not os.path.exists(os.path.join(root,fname)) or 
            getsize(os.path.join(root,fname + '.avi')) = 0 ):"""
            
    '''movnames.append(os.path.join(root, fname))'''
    '''for fname in files:
        if ('.MOV' in fname[-4:]):
            fullname = root + '/' + fname
            print fullname
            movnames.append(fullname)'''
        
    '''movnames = [os.path.join(root,fname) for fname in files if fname.endswith('.MOV')]'''