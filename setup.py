from setuptools import setup, find_packages

setup(
    name='swanapi',
    version='0.1.1',
    author='ZeYiLin',
    author_email='zeyi.lin@swanhub.co',
    description='A low threshold, high performance, compatible with a variety of different scenarios of'
                ' deep learning API image construction and reasoning tool',
    packages=find_packages(),

    entry_points={"console_scripts": ["swanapi=swanapi.make_build:build"]}
)