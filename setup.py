from setuptools import setup, find_packages
from setuptools.command.test import test
import platform
import sys
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('project.cfg')


class Tox(test):
    """
    setuptools Command
    """

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        test.initialize_options(self)
        self.tox_args = '-v'

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        err_no = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(err_no)

setup(name=config.get('Project', 'name').lower(),
      maintainer=config.get('Project', 'maintainer'),
      maintainer_email=config.get('Project', 'maintainer_email'),
      url=config.get('Project', 'url'),
      version=config.get('Project', 'release'),
      platforms=[platform.platform()],  # TODO indicate really tested platforms

      packages=find_packages(),
      install_requires=config.get('Project', 'required').split(),

      # metadata

      description=config.get('Project', 'summary'),
      long_description=open(
          config.get('Project', 'description_file'), 'r').readlines(),

      license=config.get('Project', 'licence'),

      keywords=config.get('Project', 'keywords'),

      classifiers=config.get('Project', 'classifiers').splitlines(),

      # tests

      tests_require=config.get('Test', 'required').split(),
      test_suite=config.get('Test', 'dir'),
      cmdclass={config.get('Test', 'tox_cmd'): Tox}
      )
