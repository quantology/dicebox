try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Environment :: Console",
    "Intended Audience :: Other Audience",
    "License :: OSI Approved :: BSD License",
    "Topic :: Games/Entertainment",
    "Topic :: Games/Entertainment :: Board Games",
    "Topic :: Games/Entertainment :: Role-Playing",
    "Topic :: Games/Entertainment :: Turn Based Strategy",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
    "Development Status :: 3 - Alpha",
    "Operating System :: OS Independent",
]

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(name="dicebox",
      version="0.4.0",
      author="Michael Tartre",
      author_email="michael@enkratic.com",
      url="https://github.com/quantology/dicebox",
      packages=["dicebox"],
      install_requires=["numpy"],
      extras_require={
        "parse":  ["asteval"],
        "dndsim": ["pandas"],
      },
      description="A simple python DSL for dice.",
      long_description=long_description,
      long_description_content_type='text/markdown',
      license="bsd-3-clause",
      classifiers=classifiers
      )
