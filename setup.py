#!/usr/bin/env python
from setuptools import setup

import lpd

setup(name='lpd',
      version=lpd.__version__,
      description='Longman Pronunciation Dictionary dsl data loader',
      url='https://github.com/meng89/lpd',
      license='MIT',
      author='Chen Meng',
      author_email='observerchan@gmail.com',
      py_modules=['lpd'],
      scripts=['lpd.py'],
      )
