#!/usr/bin/env python
from setuptools import setup  # type: ignore

try:
    with open('README.rst') as file:
        long_description = file.read()
except IOError:
    long_description = "missing"


setup(
    name='syntok',
    version='1.2.0',
    url='https://github.com/fnl/syntok',
    author='Florian Leitner',
    author_email='me@fnl.es',
    description='sentence segmentation and word tokenization toolkit',
    keywords='sentence segmenter splitter split word tokenizer token nlp',
    license='MIT',
    packages=['syntok'],
    install_requires=['regex'],  # handles all Unicode categories in Regular Expressions
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Linguistic',
    ],
)
