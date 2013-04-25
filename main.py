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

    # Parse any conf_file specification
    # We make this parser with add_help=False so that
    # it doesn't parse -h and print help.
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
            'source_dir': '/home/nedr/progs/convert/test_area/source',
            'old_files_dir': '/home/nedr/progs/convert/converted',
            'source_extention': '.mov',
            'dest_extention': '.avi',
            'store_path': 'yes',
            'command': 'echo',
            'options': '',
            'resursive': 'yes'}

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
    parser.add_argument('-D', '--old_files_dir',
                        help='directory to store old (unchanged) files')
    parser.add_argument('-e', '--source_extention',
                        help='source files extantion')
    parser.add_argument('-E', '--dest_extention',
                        help='extention, that changed files will have')
    parser.add_argument('-s', '--store_path',
                        help='store \'full\' or \'relative\' path of source'
                        '  files for backing up or \'dont\' save path at all'
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
             args.source_extention,
             args.source_dir,
             args.dest_extention,
             args.store_path,
             args.command,
             args.options,
             args.source_extention,
             args.old_files_dir,
             args.convert_if_result_exist,
             args.store_existing_backups)

    # search files ended with source_extention
    # At first get names of all file and dir objects
    for dirpath, dirnames, filenames in os.walk(args.source_dir):
        for filename in filenames:
            # Check every file extension (end of filename) for compliance to
            # source_extention
            if filename.lower().endswith(args.source_extention.lower()):
                source_filename = join(dirpath, filename)
                # Compile destination path and filename (overwrite if exist)
                dest_path_and_filename = source_filename + args.dest_extention
                print args.convert_if_result_exist
                if os.path.exists(dest_path_and_filename) and \
                   args.convert_if_result_exist == 'no':
                    print '%s exist, don\'t owerwrite' % dest_path_and_filename
                    continue

                print 'fr: ', source_filename
                #TODO: join 
                backup_path_and_file = join(args.old_files_dir,
                        os.path.relpath(dirpath, args.source_dir),
                        dest_path_and_filename)
                print 'to: ', backup_path_and_file
                if os.path.exists(backup_path_and_file) is True:
                    print dest_path_and_filename, ' exist'

                if os.path.exists(source_filename) is True:
                    print source_filename, 'exist'

                if args.store_path is 'full':
                    backup_dirname = join(args.old_files_dir, dirpath)
                elif args.store_path is 'relative':
                    backup_dirname = join(args.old_files_dir, dirnames)
                elif args.store_path is 'not':
                    backup_dirname = args.old_files_dir
                dest_path_and_filename = filename + args.dest_extention

                #TODO: move it after converting or remove it
                if os.path.exists(join(backup_dirname,
                                       dest_path_and_filename)):
                    if args.store_existing_backups is False:
                        os.remove(dest_path_and_filename)
                    else:
                        continue

                print dirpath
                print filename
                print source_filename
                # Call command. Subprocess.call return non-zero if error
                # occurs, whithout exception
                if subprocess.call([args.command, source_filename,
                                    dest_path_and_filename, args.options]):
                    logging.error('Error while converting %s' % source_filename)
                else:
                    logging.info('%s converted successfully', source_filename)
                # backup folder existing check and moving .mov to it
                if not os.access(backup_dirname, os.F_OK):
                    os.makedirs(args.old_files_dir + dirpath, 0700)
                backup_filename = args.old_files_dir + source_filename
                if os.access(backup_filename, os.F_OK):
                    os.remove(backup_filename)
                    logging.info('old backup file %s was removed!',
                                 backup_filename)
                else:
                    os.rename(source_filename, backup_filename)

    return(0)

if __name__ == "__main__":
    sys.exit(main())
