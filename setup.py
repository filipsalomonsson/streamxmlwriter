#!/usr/bin/env python
from distutils.core import setup
# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

import streamxmlwriter

setup(name="streamxmlwriter",
      version=streamxmlwriter.__version__,
      description="Simple library for incrementally writing XML files of arbitrary size",
      long_description=streamxmlwriter.__doc__,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Text Processing :: Markup :: XML",
        ],
      author="Filip Salomonsson",
      author_email="filip.salomonsson@gmail.com",
      url="http://github.com/infixfilip/streamxmlwriter/tree/master",
      py_modules=["streamxmlwriter"],
      license="MIT",
      )
