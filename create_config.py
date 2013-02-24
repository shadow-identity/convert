# Creates simple config file

import ConfigParser
config = ConfigParser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.

config.add_section('Main')
config.set('Main', 'source_dir', '/home/nedr/progs/convert/test_area')
config.set('Main', 'recursive', 'yes')
config.set('Main', 'verbose', 'no')
config.set('Main', 
           'old_files_dir', '/home/nedr/progs/convert/test_area/converted')
config.set('Main', 'source_extention', '.mov')
config.set('Main', 'dest_extention', '.avi')
config.set('Main', 'command', 'cp')
config.set('Main', 'options', '--interactive')

# Writing our configuration file to 'example.cfg'
with open('example.cfg', 'wb') as configfile:
    config.write(configfile)