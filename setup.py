from setuptools import setup, find_packages

NAME = "shlomobot_pytest"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name=NAME,
    version=VERSION,
    description="ShlomoBOT helper library for test files",
    author_email="",
    url="https://github.com/DARTSG/shlomobot_pytest",
    keywords=["ShlomoBOT", "Pytest"],
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    ShlomoBOT helper library for test files
    """,
)
