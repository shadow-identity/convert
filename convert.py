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

def get_backup_path_filename(store_path, backup_directory,
                             source_path_filename, source_dir,
                             dirpath, filename):
    """ According to args.store_path calculate full destination file-
      and directory name
    """
    #TODO: join
    #TODO: check store_path var
    if store_path == 'full':
        return (os.path.abspath(backup_directory) + source_path_filename,
                os.path.abspath(backup_directory) + dirpath)
    elif store_path == 'relative':
        return (os.path.join(backup_directory,
                             os.path.relpath(source_path_filename,
                                             source_dir)),
                os.path.join(backup_directory,
                             os.path.relpath(dirpath, source_dir)))
    else:
        return (os.path.join(backup_directory, filename),
                backup_directory)
    '''backup_path_filename = join(args.backup_directory,
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
            'act_original': 'move',
            'backup_directory': '/home/nedr/progs/convert/backup',
            'source_extension': '.mov',
            'dest_extension': '.avi',
            'store_path': 'relative',
            'command': 'cp',
            'options': '-T',
            'dest_as_dir': False,
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
    parser.add_argument('-D', '--backup_directory',
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
    parser.add_argument('--dest_as_dir',
                        help='take to command directory name instead of filename as target',
                        action='store_true')

    args = parser.parse_args(remaining_argv)
    logging.basicConfig(level=logging.INFO, filename='convert.log', filemode='w')


def call_command(command, source_path_filename, dest_path_filename, options):
    """Call command. Subprocess.call return non-zero if error
    occurs, without exception"""
    print ('calling with args:\ncommand: {command} options: {op}\n'
           'source path: {sp}\ndestination path: {dp}\n').format(command=command,
                                                                 op=options,
                                                                 sp=source_path_filename,
                                                                 dp=dest_path_filename
    )
    result = subprocess.call([command,  options, source_path_filename,
                        dest_path_filename])
    if result:
        logging.error('Error while converting %s' % source_path_filename)
    else:
        logging.info('%s converted successfully', source_path_filename)
    return result

def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

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
        args.backup_directory,
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

                if (os.path.exists(dest_path_filename) and 
                        args.convert_if_result_exist == 'no'):
                    print ('destination %s exist, don\'t overwrite'
                           % dest_path_filename)
                    continue

                print 'from: ', source_path_filename
                print 'to  : ', dest_path_filename

                # check if destination exist
                if not os.path.exists(dest_path_filename) or (
                        os.path.exists(dest_path_filename) and args.convert_if_result_exist):
                    # no output file or 'convert if result exist' is set: execute command
                    if args.convert_if_result_exist is True:
                        # remove existing file
                        os.remove(dest_path_filename)
                        print 'remove existing destination'
                    if args.dest_as_dir:
                        result = call_command(args.command, source_path_filename, dirpath, args.options)
                    else:
                        result = call_command(args.command, source_path_filename, dest_path_filename, args.options)

                # backup folder existing check and moving .mov to it
                #TODO: act_original check
                if not result:
                    if args.act_original == 'move':
                        backup_path_filename, backup_path_dir = get_backup_path_filename(
                            store_path=args.store_path,
                            backup_directory=args.backup_directory,
                            source_path_filename=source_path_filename,
                            source_dir=args.source_dir,
                            dirpath=dirpath,
                            filename=filename
                        )
                        print 'back: ', backup_path_filename

                        if not os.access(backup_path_dir, os.F_OK):
                            os.makedirs(args.backup_directory + dirpath, 0700)
                        if os.access(backup_path_filename, os.F_OK):
                            os.remove(backup_path_filename)
                            logging.info('old backup file %s was removed!',
                                         backup_path_filename)
                        else:
                            os.rename(source_path_filename, backup_path_filename)
                    elif args.act_original == 'delete':
                        if os.access(source_path_filename, os.F_OK):
                            os.remove(source_path_filename)
                            logging.info('original file %s was removed',
                                         source_path_filename)
                        else:
                            logging.info('can\'t get access to %s to remove',
                                         source_path_filename)

    return 0

if __name__ == "__main__":
    sys.exit(main())