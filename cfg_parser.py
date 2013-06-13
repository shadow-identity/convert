import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read(['example.cfg'])
defaults = dict(config.items("Main"))
print defaults
print config.getboolean("Main", "dest_as_dir")