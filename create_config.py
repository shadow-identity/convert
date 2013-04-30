""" Creates simple example config file for convert.py, named "example.cfg" """

import ConfigParser
config = ConfigParser.RawConfigParser()

config.add_section('Main')
config.set('Main', 'source_dir', '/home/nedr/progs/convert/test_area/source')
#FIXME: how to turn it into boolean?
config.set('Main', 'convert_if_result_exist', 'no')
config.set('Main', 'recursive', 'yes')
config.set('Main', 'verbose', 'No')
config.set('Main',
           'old_files_dir', '/home/nedr/progs/convert/test_area/converted')
config.set('Main', 'source_extention', '.mov')
config.set('Main', 'dest_extention', '.avi')
config.set('Main', 'store_path', 'full')
config.set('Main', 'store_existing_backups', 'yes')
config.set('Main', 'command', 'cp')
config.set('Main', 'options', '--interactive')

# Writing our configuration file to 'example.cfg'
with open('example.cfg', 'wb') as configfile:
    config.write(configfile)
