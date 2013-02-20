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

import os, subprocess, logging, datetime
from os.path import join, getsize

logging.basicConfig(level = logging.INFO, filename = 'convert.log')
source_dir = '/home/nedr/progs/convert/test_area'
old_files_dir = '/home/nedr/progs/convert/test_area/converted'
source_extention = '.mov'
dest_extention = '.avi'
command = 'ffmpeg'
options = ''
logging.info('''== %s === 
converting %s
from       %s
to         %s
using      %s %s
backups of %s moves to %s
     saving full path''', 
             datetime.datetime.now().strftime("%Y %B %d %I:%M%p"),
             source_extention, source_dir, dest_extention, command, options,
             source_extention, old_files_dir)


# searching files ended with source_extention
for dirpath, dirnames, filenames in os.walk(source_dir):
    for filename in filenames:
        sourcefilename = join(dirpath, filename)
        destfilename = join(dirpath, filename + dest_extention)
        if (filename.lower().endswith(source_extention.lower()) and 
            not (os.path.exists(destfilename)
            and getsize(destfilename) != 0)):
            if subprocess.call(['echo', command, sourcefilename, destfilename,
                                options]):
                logging.error('Error while converting %s' %sourcefilename)
            # backup folder existing check and movin
            if not os.access(old_files_dir + dirpath, os.F_OK):
                os.makedirs(old_files_dir + dirpath,0700)
            os.rename(sourcefilename, old_files_dir + sourcefilename)