import ConfigParser
config = ConfigParser.ConfigParser()
config.read('project.cfg')

__version__ = config.get('Project', 'release'),