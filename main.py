# -*- coding: utf-8 -*-
"""
Seek target files in directoryes and run defined command according config or
command line arguments (arguments overrides config file parameters).

!NB: processing existing files (store/overwrite/error) depends on the behavior
of the program

main
wk_dir = root
    os.walk (root, dirs, files)
    search *.mov in files
        yes: run convert root+files[i]
            move *.mov into thrash dir saving original pathname to easy backup

@author: nedr
"""
#TODO: logging to file (verbose)
#TODO: exceptions

import os
import subprocess
import logging
import datetime
import argparse
import ConfigParser
from os.path import join
import sys


def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    def get_backup_path_filename(store_path, original_files_dir,
                                 source_path_filename, source_dir, filename):
        #TODO: join
        #TODO: check store_path var
        if store_path == 'full':
            return os.path.abspath(original_files_dir) + source_path_filename
        elif store_path == 'relative':
            return (os.path.join(original_files_dir,
                                 os.path.relpath(source_path_filename,
                                                 source_dir)))
        else:
            return os.path.join(original_files_dir, filename)
        '''backup_path_filename = join(args.original_files_dir,
                os.path.relpath(dirpath, args.source_dir),
                dest_path_filename)'''

    def conf_arg_parser():
        """Parse any conf_file specification
        We make this parser with add_help=False so that
        it doesn't parse -h and print help."""

        global args
        conf_parser = argparse.ArgumentParser(
            # Don't mess with format of description
            formatter_class=argparse.RawDescriptionHelpFormatter,
            # Turn off help, so we print all options in response to -h
            add_help=False)
        conf_parser.add_argument("--conf_file",
                                 help="Specify config file", metavar="FILE")
        args, remaining_argv = conf_parser.parse_known_args()

        if args.conf_file:
            config = ConfigParser.SafeConfigParser()
            config.read([args.conf_file])
            defaults = dict(config.items("Main"))
        else:
            defaults = {
                'source_dir': '/home/nedr/progs/convert/test_area',
                'original_files_dir': '/home/nedr/progs/convert/converted',
                'source_extension': '.mov',
                'dest_extension': '.avi',
                'store_path': 'full',
                'command': 'echo',
                'options': '',
                'recursive': 'yes',
                'backup_originals': 'yes'}

        # Parse rest of arguments
        parser = argparse.ArgumentParser(
            description=__doc__,
            # Inherit options from config_parser
            parents=[conf_parser])

        parser.set_defaults(**defaults)

        parser.add_argument('-d', '--source_dir',
                            help='source directory, searching begins from')
        parser.add_argument('--convert_if_result_exist',
                            help='if not - skip them', action='store_true')
        parser.add_argument('-r', '--recursive',
                            help='recursive search, not implemented yet',
                            action='store_true')
        parser.add_argument('-v', '--verbose', help='increase output verbosity',
                            action='store_true')
        parser.add_argument('-b', '--act_original',
                            help='action with the original file: '
                                 'ignore (and leave), '
                                 'move to backup directory '
                                 'or delete from disk',
                            choices=['ignore', 'move', 'delete'])
        parser.add_argument('-D', '--original_files_dir',
                            help='directory to backup original (unchanged) files')
        parser.add_argument('-e', '--source_extension',
                            help='source files extension')
        parser.add_argument('-E', '--dest_extension',
                            help='extension, that changed files will have')
        parser.add_argument('-s', '--store_path',
                            help='store \'full\' or \'relative\' path of source'
                            ' files for backing up or \'dont\' save path at all'
                            ' (dangerous)',
                            choices=['full', 'relative', 'dont'])
        parser.add_argument('-f', '--store_existing_backups',
                            help='don\'t overwrite existing backups',
                            action='store_true')
        parser.add_argument('-c', '--command', help='converting command')
        parser.add_argument('-o', '--options',
                            help='options of converting command')
        args = parser.parse_args(remaining_argv)
        logging.basicConfig(level=logging.INFO, filename='convert.log')

    def call_command():
        if subprocess.call([args.command, source_path_filename,
                            dest_path_filename, args.options]):
            logging.error('Error while converting %s' % source_path_filename)
        else:
            logging.info('%s converted successfully', source_path_filename)

    conf_arg_parser()
    print args

    logging.info(
        '''== %s ===
    converting %s
    from       %s
    to         %s (store path = %s)
    using      %s %s
    backups of %s moves to %s
    overwrite existing converted files: %s
    store path: %s''',
        datetime.datetime.now().strftime("%Y %B %d %I:%M%p"),
        args.source_extension,
        args.source_dir,
        args.dest_extension,
        args.store_path,
        args.command,
        args.options,
        args.source_extension,
        args.original_files_dir,
        args.convert_if_result_exist,
        args.store_existing_backups)

    # search files ended with source_extension
    # At first get names of all file and directory objects
    for dirpath, dirnames, filenames in os.walk(args.source_dir):
        for filename in filenames:
            # Check every file extension (end of filename) for compliance to
            # source_extension
            if filename.lower().endswith(args.source_extension.lower()):
                source_path_filename = join(dirpath, filename)
                #FIX: wtf is '(overwrite if exist)'?
                # Compile destination path and filename (overwrite if exist)
                dest_path_filename = source_path_filename + args.dest_extension
                print args.convert_if_result_exist

                if (os.path.exists(dest_path_filename) and 
                        args.convert_if_result_exist == 'no'):
                    print ('destination %s exist, don\'t overwrite'
                           % dest_path_filename)
                    continue

                backup_path_filename = get_backup_path_filename(
                    store_path=args.store_path,
                    original_files_dir=args.original_files_dir,
                    source_path_filename=source_path_filename,
                    source_dir=args.source_dir,
                    filename=filename
                )
                print 'from: ', source_path_filename
                print 'to  : ', dest_path_filename
                print 'back: ', backup_path_filename

                # check if destination exist
                if not os.path.exists(dest_path_filename) or (
                        os.path.exists(dest_path_filename) and args.convert_if_result_exist):
                    # no output file or 'convert if result exist' is set: execute command
                    if args.convert_if_result_exist is True:
                        # remove existing file
                        os.remove(dest_path_filename)
                        print 'remove existing destination'
                    call_command()
                    print 'doing job'

                # Call command. Subprocess.call return non-zero if error
                # occurs, without exception

                # backup folder existing check and moving .mov to it
                #TODO: store existing backups if needed
                #TODO: act_original check

                if not os.access(backup_path_filename, os.F_OK):
                    os.makedirs(args.original_files_dir + dirpath, 0700)
                backup_filename = args.original_files_dir + source_path_filename
                if os.access(backup_filename, os.F_OK):
                    os.remove(backup_filename)
                    logging.info('old backup file %s was removed!',
                                 backup_filename)
                else:
                    os.rename(source_path_filename, backup_filename)

                # check if backup exist
                if os.path.exists(backup_path_filename) is True:
                    print backup_path_filename, ' exist'



    return 0

if __name__ == "__main__":
    sys.exit(main())

'''
                if args.store_path is 'full':
                    backup_dirname = join(args.original_files_dir, dirpath)
                elif args.store_path is 'relative':
                    backup_dirname = join(args.original_files_dir, dirnames)
                elif args.store_path is 'not':
                    backup_dirname = args.original_files_dir
                
                #TODO: move it after converting or remove it
                if os.path.exists(join(backup_dirname,
                                       dest_path_filename)):
                    if args.store_existing_backups is False:
                        os.remove(dest_path_filename)
                    else:
                        continue

                print dirpath
                print filename
                print source_path_filename
                
'''