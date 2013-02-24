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

import os, subprocess, logging, datetime, argparse, ConfigParser
from os.path import join

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help = 'increase output verbosity',
                    action='store_true')
parser.add_argument('-s', '--source_dir', 
                    help = 'source directory, searching begins from')
parser.add_argument('-o', '--old_files_dir', 
                    help = 'directory to store old (unchanged) files')
parser.add_argument('-e', '--source_extention', help = 'source files extantion')
parser.add_argument('-E', '--dest_extention', 
                    help = 'extention, that changed files will have')
parser.add_argument('-c', '--command', help = 'converting command')
parser.add_argument('-O', '--options', help = 'options of converting command')
parser.add_argument('-r', '--recursive', help = 'recursive search',
                    action = 'store_true')
parser.add_argument('--config', help = 'path to configuration file')
args = parser.parse_args()

if args.config:
    config = ConfigParser.RawConfigParser()
    config.read(args.config)
    
    if args.source_dir: config = args.source_dir
    else: source_dir = config.get('Main', 'source_dir')
    if args.recursive: recursive = args.recursive
    else: recursive = config.getboolean('Main', 'recursive')
    config.getboolean('Main', 'verbose')
    config.get('Main', 'old_files_dir')
    config.get('Main', 'source_extention')
    config.get('Main', 'dest_extention')
    config.get('Main', 'command')
    config.get('Main', 'options')
    
logging.basicConfig(level = logging.INFO, filename = 'convert.log')

source_dir = '/home/nedr/progs/convert/test_area'
old_files_dir = '/home/nedr/progs/convert/test_area/converted'
source_extention = '.mov'
dest_extention = '.avi'
command = 'echo'
options = ''
logging.info('''== %s === 
converting %s
from       %s
to         %s
using      %s %s
backups of %s moves to %s
     saving full path, OVERWRITING existing files''', 
             datetime.datetime.now().strftime("%Y %B %d %I:%M%p"),
             source_extention, source_dir, dest_extention, command, options,
             source_extention, old_files_dir)


# searching files ended with source_extention
for dirpath, dirnames, filenames in os.walk(source_dir):
    for filename in filenames:
        sourcefilename = join(dirpath, filename)
        if filename.lower().endswith(source_extention.lower()):
            destfilename = join(dirpath, filename + dest_extention)
            if os.path.exists(destfilename):
                os.remove(destfilename)
            print dirpath
            print filename
            print sourcefilename
            if subprocess.call([command, sourcefilename, destfilename,
                                options]):
                logging.error('Error while converting %s' %sourcefilename)
            else:
                logging.info('%s converted successfully', sourcefilename)
            # backup folder existing check and moving .mov to it
            if not os.access(old_files_dir + dirpath, os.F_OK):
                os.makedirs(old_files_dir + dirpath,0700)
            backup_filename = old_files_dir + sourcefilename 
            if os.access(backup_filename, os.F_OK):
                os.remove(backup_filename)
                logging.info('old backup file %s was removed!', backup_filename)
            else:
                os.rename(sourcefilename, backup_filename)

#rsync