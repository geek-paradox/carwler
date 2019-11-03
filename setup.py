from setuptools import setup, find_packages

setup(
    name='carwler',
    version='1.0',
    packages=find_packages(),
    install_requires=['flask', 'beautifulsoup4', 'requests', 'pymongo']
)
