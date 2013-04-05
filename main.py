# -*- coding: utf-8 -*-
"""
Seek target files in directoryes and run defined command according config or
command line arguments (arguments overrides config file parameters).

main
wk_dir = root
    os.walk (root, dirs, files)
    search *.mov in files
        yes: run convert root+files[i]
            move *.mov into thrash dir saving original pathname to easy backup

@author: nedr
"""



#TODO: logging to file (verbose)
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
        description=__doc__,
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Turn off help, so we print all options in response to -h
        add_help=False
        )
    conf_parser.add_argument("-c", "--conf_file",
                        help="Specify config file", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    if args.conf_file:
        config = ConfigParser.SafeConfigParser()
        config.read([args.conf_file])
        defaults = dict(config.items("Main"))
    else:
        defaults = {"source_dir": "default"}

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser]
        )
    parser.set_defaults(**defaults)

    parser.add_argument('-v', '--verbose', help='increase output verbosity',
                        action='store_true')
    parser.add_argument('-s', '--source_dir',
                        help='source directory, searching begins from')
    parser.add_argument('-o', '--old_files_dir',
                        help='directory to store old (unchanged) files')
    parser.add_argument('-e', '--source_extention',
                        help='source files extantion')
    parser.add_argument('-E', '--dest_extention',
                        help='extention, that changed files will have')
    parser.add_argument('--command', help='converting command')
    parser.add_argument('-O', '--options',
                        help='options of converting command')
    parser.add_argument('-r', '--recursive', help='recursive search',
                        action='store_true')

    args = parser.parse_args(remaining_argv)
    print "source_dir is \"{}\"".format(args.source_dir)

    logging.basicConfig(level=logging.INFO, filename='convert.log')

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
    """for dirpath, dirnames, filenames in os.walk(source_dir):
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
                    logging.error('Error while converting %s' % sourcefilename)
                else:
                    logging.info('%s converted successfully', sourcefilename)
                # backup folder existing check and moving .mov to it
                if not os.access(old_files_dir + dirpath, os.F_OK):
                    os.makedirs(old_files_dir + dirpath, 0700)
                backup_filename = old_files_dir + sourcefilename
                if os.access(backup_filename, os.F_OK):
                    os.remove(backup_filename)
                    logging.info('old backup file %s was removed!',
                                 backup_filename)
                else:
                    os.rename(sourcefilename, backup_filename)"""

    return(0)

if __name__ == "__main__":
    sys.exit(main())
