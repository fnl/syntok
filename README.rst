======
syntok
======

(a.k.a. segtok_ v2)

.. image:: https://img.shields.io/pypi/v/syntok.svg
    :alt: syntok version
    :target: https://pypi.python.org/pypi/syntok

.. image:: https://github.com/fnl/syntok/actions/workflows/tox.yaml/badge.svg
    :alt: tox build
    :target: https://github.com/fnl/syntok/actions/workflows/tox.yaml

-------------------------------------------
Sentence segmentation and word tokenization
-------------------------------------------

The syntok package provides two modules, ``syntok.segmenter`` and ``syntok.tokenizer``.
The tokenizer provides functionality for splitting (Indo-European) text into words and symbols (collectively called *tokens*).
The segmenter provides functionality for splitting (Indo-European) token streams (from the tokenizer) into sentences and for pre-processing documents by splitting them into paragraphs.
Both modules can also be used from the command-line to split either a given text file (argument) or by reading from STDIN.
While other Indo-European languages could work, it has only been designed with the languages Spanish, English, and German in mind (the author's main languages).

``segtok``
==========

Syntok is the successor of an earlier, very similar tool, segtok_, but has evolved significantly in terms of providing better segmentation and tokenization performance and throughput (syntok can segment documents at a rate of about 100k tokens per second without problems).
For example, if a sentence terminal marker is not followed by a spacing character, segtok is unable to detect that as a terminal marker, while syntok has no problem segmenting that case (as it uses tokenization first, and does segmentation afterwards).
In fact, I feel confident enough to just boldly claim syntok is the world's best sentence segmenter for at least English, Spanish, and German.

Installation
============

To use this package, you minimally should have Python 3.6 or installed.
As it uses the typing package, earlier versions are not supported.
The easiest way to get ``syntok`` installed is using ``pip`` or any other package manager that works with PyPI::

    pip3 install syntok

*Important*: If you are on **Linux** and have problems installing the ``regex`` dependency of ``syntok``, make sure you have the ``python-dev`` and/or ``python3-dev`` packages installed to get the necessary headers to compile that package.

Then try the command line tools on some plain-text files (e.g., this README) to see if ``syntok`` meets your needs::

    python3 -m syntok.segmenter README.rst
    python3 -m syntok.tokenizer README.rst

Development
===========

``syntok`` uses poetry_ as the build tool, and expects pyenv_ to provide the Python versions to test with tox_.
Therefore, to develop ``syntok``, it is recommended that you install Poetry and pyenv, first.
Install the Python versions defined in ``tox.ini`` (see ``envlist``) with pyenv, and set all of them as your local versions, for example: ``pyenv local 3.6.15 3.9.9``

To run the full test suite, you have to install flake8_, pytest_, and mypy_ (via ``poetry install``).
The tests in the proper Python version & environment are run via ``tox`` or by calling the three commands by hand::

   poetry run tox

   # OR, manually:
   poetry shell
   flake8 syntok
   mypy syntok
   pytest syntok

Usage
=====

For details, please refer to the code documentation; This README only provides an overview of the provided functionality.

Command-line
------------

After installing the package, two command-line usages will be available, ``python -m syntok.segmenter`` and ``python -m syntok.tokenizer``.
Each takes [UTF-8 encoded] plain-text files (or STDIN until EOF (CTRL-D)) as input and transforms that into newline-separated sentences or space-separated tokens, respectively.
You can control Python3's file ``open`` encoding by `configuring the environment variable`_ ``PYTHONIOENCODING`` to your needs (e.g. ``export PYTHONIOENCODING="utf-16-be"``).
The tokenizer produces single-space separated tokens for each input line.
The segmenter produces line-segmented sentences for each input file (or after STDIN closes).

``syntok.tokenizer``
--------------------

This module provides the ``Tokenizer`` class to tokenize input text into words and symbols (**value** Tokens), prefixed with (possibly empty) **spacing** strings, while recording their **offset** positions.
The Tokenizer comes with utility static functions, to join hyphenated words across line-breaks, and to reproduce the original string from a sequence of tokens.
The Tokenizer considers camelCase words as individual tokens (here: camel and Case) and by default considers underscores and Unicode hyphens *inside* words as spacing characters (not Token values).
It does not split numeric tokens (without letters) if they contain symbols (e.g. maintaining "2018-11-11", "12:30:21", "1_000_000", "1,000.00", or "1..3" all as single tokens)
Finally, as it splits English negation contractions (such as "don't") into their root and "not" (here: do and not), it can be configured to refrain from replacing this special "n't" token with "not", and instead emit the actual "n't" value.

To track the spacing and offset of tokens, the module contains the ``Token`` class, which is a ``str`` wrapper class where the token **value** itself is available from the ``value`` property and adding a ``spacing`` and a ``offset`` property that will hold the **spacing** prefix and the **offset** position of the token, respectively.

Basic example::

   from syntok.tokenizer import Tokenizer

   document = open('README.rst').read()
   tok = Tokenizer()  # optional: keep "n't" contractions and "-", "_" inside words as tokens

   for token in tok.tokenize(document):
       print(repr(token))

``syntok.segmenter``
--------------------

This module provides several functions to segment documents into iterators over paragraphs, sentences, and tokens (functions ``analyze`` and ``process``) or simply sentences and tokens (functions ``split`` and ``segment``).
The analytic segmenter can even keep track of the original offset of each token in the document while processing (but does not join hyphen-separated words across line-breaks).
All segmenter functions accept arbitrary Token streams as input (typically as generated by the ``Tokenizer.tokenize`` method).
Due to how ``syntok.tokenizer.Token`` objects "work", it is possible to establish the exact sentence content (with the original spacing between the tokens).
The pre-processing functions and paragraph-based segmentation splits paragraphs, i.e., chunks of text separated by at least two consecutive linebreaks (``\\r?\\n``).

Basic example::

   import syntok.segmenter as segmenter

   document = open('README.rst').read()

   # choose the segmentation function you need/prefer

   for paragraph in segmenter.process(document):
       for sentence in paragraph:
           for token in sentence:
               # roughly reproduce the input,
               # except for hyphenated word-breaks
               # and replacing "n't" contractions with "not",
               # separating tokens by single spaces
               print(token.value, end=' ')
           print()  # print one sentence per line
       print()  # separate paragraphs with newlines

   for paragraph in segmenter.analyze(document):
       for sentence in paragraph:
           for token in sentence:
               # exactly reproduce the input
               # and do not remove "imperfections"
               print(token.spacing, token.value, sep='', end='')
       print("\n")  # reinsert paragraph separators

Legal
=====

License: `MIT <http://opensource.org/licenses/MIT>`_

Copyright (c) 2017-2022, Florian Leitner. All rights reserved.

Contributors
============

- Arjen P. de Vries, @arjenpdevries, http://www.cs.ru.nl/~arjen/
- Bastian Zimmermann, @BastianZim
- Péter Láng, @peter-lang-dealogic
- Koen Dercksen, @KDercksen, https://koendercksen.com/
- Sergiusz Bleja, @svenski

Thank you!

History
=======

- **1.4.4** bug fixes: support for single letter consontant abbreviations, "Min.", and "Sen." `#26`_ and German weekday abbreviations
- **1.4.3** bug fixes: under-splitting at month abbreviations `#22`_ and over-splitting at "no." abbreviations `#21`_
- **1.4.2** improved handling of parenthesis at start of sentences and bugfix for citations at end of texts `#19`_
- **1.4.1** support citations at sentence begin (e.g., Bible quotes) `#12`_
- **1.4.0** migrated to pyproject.toml and tox.ini, dropped Makefile builds and Py3.5 support
- **1.3.3** splitting tokens around the zero-width space characater U+200B `#18`_
- **1.3.2** bugfix for offset of not contractions; discussion in Issue `#15`_
- **1.3.1** segmenting now occurs at semi-colons, too; discussion in Issue `#9`_
- **1.2.2** bugfix for offsets in multi-nonword prefix tokens; Issue `#6`_
- **1.2.1** added a generic rule for catching more uncommon uses of "." without space suffix as abbreviation marker
- **1.2.0** added support for skipping and handling text in brackets (e.g., citations)
- **1.1.1** fixed non-trivial segmentation in sci. text and refactored splitting logic to one place only
- **1.1.0** added support for ellipses (back - from segtok) in
- **1.0.2** hyphen joining only should happen when letters are present; squash escape warnings
- **1.0.1** fixing segmenter.analyze to preserve "n't" contractions, and improved the README and Tokenizer constructor API
- **1.0.0** initial release

.. _configuring the environment variable: https://docs.python.org/3/using/cmdline.html
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _poetry: https://python-poetry.org/
.. _segtok: https://github.com/fnl/segtok
.. _mypy: http://mypy-lang.org/
.. _pyenv: https://github.com/pyenv/pyenv
.. _pytest: https://docs.pytest.org/en/latest/
.. _tox: https://tox.wiki/en/latest/
.. _#6: https://github.com/fnl/syntok/issues/6
.. _#9: https://github.com/fnl/syntok/issues/9
.. _#12: https://github.com/fnl/syntok/pull/12
.. _#15: https://github.com/fnl/syntok/issues/15
.. _#18: https://github.com/fnl/syntok/pull/18
.. _#19: https://github.com/fnl/syntok/issues/19
.. _#21: https://github.com/fnl/syntok/issues/21
.. _#22: https://github.com/fnl/syntok/issues/22
.. _#26: https://github.com/fnl/syntok/issues/26
