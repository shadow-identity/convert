# -*- coding: utf-8 -*-
"""
Seek target files in directoryes and run defined command according config or
command line arguments (arguments overrides config file parameters).

!NB: processing existing files (store/overwrite/error) depends on the behavior
of the program

This is a BAD program. It does not meet requirements of the KISS principle. It is not pythonic.
It's so sad.

@author: nedr
"""
#TODO: exceptions

import os
import subprocess
import logging
import datetime
import argparse
import ConfigParser
from os.path import join
import sys
import hashlib


def get_backup_path_filename(store_path, backup_directory,
                             source_path_filename, source_dir,
                             dirpath, filename):
    """ According to args.store_path calculate full destination file-
      and directory name
    """
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
            'convert_if_result_exist': True,
            'recursive': True,
            'act_original': 'move',  # ['ignore', 'move', 'delete']
            'backup_directory': '/home/nedr/progs/convert/backup',
            'source_extension': '.mov',
            'dest_extension': '.avi',
            'store_path': 'relative',  # ['full', 'relative', 'dont']
            'command': 'cp',
            'options': '-T',
            'dest_as_dir': False,
            }

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
    parser.add_argument('-c', '--command', help='converting command')
    parser.add_argument('-o', '--options',
                        help='options of converting command')
    parser.add_argument('--dest_as_dir',
                        help='take to command directory name instead of filename as target',
                        action='store_true')

    args = parser.parse_args(remaining_argv)
    logging.basicConfig(level=logging.INFO, filename='convert.log')


def call_command(command, source_path_filename, dest_path_filename, options):
    """Call command. Subprocess.call return non-zero if error
    occurs, without exception"""
    logging.info('calling command: %s options: %s '
                 'source path: %s destination path: %s',
                 command, options, source_path_filename, dest_path_filename)
    result = subprocess.call([command,  options, source_path_filename,
                              dest_path_filename])
    if result:
        logging.error('Error %i while converting %s' % (result, source_path_filename))
    else:
        logging.info('%s converted SUCCESSFULLY', source_path_filename)
    return result


def md5Checksum(file_path):
    """ Calculate md5 hash of given file
    """
    with open(file_path, 'rb') as file_contents:
        file_hash = hashlib.md5()
        while True:
            file_part = file_contents.read(8192)
            if not file_part:
                break
            file_hash.update(file_part)
        return file_hash.hexdigest()


def identity_verification(file1, file2):
    """
    Checks that file1 and file2 are the same.
    At first - by size, then by md5
    """
    if os.stat(file1).st_size == os.stat(file2).st_size:
        hash1 = md5Checksum(file1)
        hash2 = md5Checksum(file2)
        if hash1 == hash2:
            return 'same'
    return 'different'


def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    conf_arg_parser()
    print args

    logging.info(
    '''=== %s ===
    converting %s to %s
    from       %s (recursive: %s)
    using      %s %s
    second argument is directory (True) or file (False)? %s
    if destination exist it'll be overwritten? %s
    original files are %sd
    backups moves to %s
    (%s path stored)''',
            datetime.datetime.now().strftime("%Y %B %d %I:%M%p"),
            args.source_extension, args.dest_extension,
            args.source_dir, args.recursive,
            args.command, args.options,
            args.dest_as_dir,
            args.convert_if_result_exist,
            args.act_original,
            args.backup_directory,
            args.store_path)

    # search files ended with source_extension
    # At first get names of all file and directory objects
    for dirpath, dirnames, filenames in os.walk(args.source_dir):
        logging.info('Scanning %s', dirpath)
        for filename in filenames:
            # Check every file extension (end of filename) for compliance to
            # source_extension
            if filename.lower().endswith(args.source_extension.lower()):
                source_path_filename = join(dirpath, filename)
                #FIX: wtf is '(overwrite if exist)'?
                # Compile destination path and filename (overwrite if exist)
                dest_path_filename = source_path_filename + args.dest_extension

                logging.info('from: %s', filename)
                logging.info('to  : %s', dest_path_filename)

                # check if destination exist
                if not os.path.exists(dest_path_filename) or (
                        os.path.exists(dest_path_filename) and args.convert_if_result_exist):
                    # execute command (first deleting the file if needed)
                    if os.path.exists(dest_path_filename) and args.convert_if_result_exist:
                        # delete existing file
                        os.remove(dest_path_filename)
                        logging.warning('removed existing destination %s', dest_path_filename)
                    if args.dest_as_dir:
                        result = call_command(args.command, source_path_filename, dirpath, args.options)
                    else:
                        result = call_command(args.command, source_path_filename, dest_path_filename, args.options)

                    if not result:
                        # command returns 0 - do backup job
                        print '{} created'.format(dest_path_filename)
                        if args.act_original == 'move':
                            backup_path_filename, backup_path_dir = get_backup_path_filename(
                                store_path=args.store_path,
                                backup_directory=args.backup_directory,
                                source_path_filename=source_path_filename,
                                source_dir=args.source_dir,
                                dirpath=dirpath,
                                filename=filename
                            )
                            logging.info('backup: %s', backup_path_filename)

                            if not os.access(backup_path_dir, os.F_OK):
                                os.makedirs(backup_path_dir, 0700)

                            if not os.access(backup_path_filename, os.F_OK):
                                os.rename(source_path_filename, backup_path_filename)
                            else:
                                # check that the original and backupped files are the same
                                files = identity_verification(backup_path_filename,
                                                              source_path_filename)
                                if files == 'same':
                                    os.remove(source_path_filename)
                                elif files == 'different':
                                    logging.error('Original file %s and old backup file %s are different! '
                                                  'Both files are stored. Needs manual reconcile',
                                                  source_path_filename, backup_path_filename)
                                    print ('WARNING: original file {} and old backup file {} are different. '
                                           'Both files are stored. Needs manual reconcile').\
                                        format(source_path_filename, backup_path_filename)
                        elif args.act_original == 'delete':
                            if os.access(source_path_filename, os.F_OK):
                                os.remove(source_path_filename)
                                logging.warning('original file %s was removed',
                                                source_path_filename)
                            else:
                                logging.error('can\'t get access to %s to remove',
                                              source_path_filename)
                else:
                    # destination already exist and we not allowed to rewrite it
                    logging.warning('SKIP %s (destination already exist)', source_path_filename)
                    print 'SKIP {} (see logs)'.format(source_path_filename)
        if not args.recursive:
            logging.warning('Search was not recursive - exit')
            print 'Search was not recursive - exit'
            break
    return 0

if __name__ == "__main__":
    sys.exit(main())