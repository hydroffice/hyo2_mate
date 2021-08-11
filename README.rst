.. note::
   This repo is **DEPRECATED**. Go to the `new Mate repo <https://github.com/ausseabed/mate>`_.

Mate
====

.. image:: https://ci.appveyor.com/api/projects/status/f3c5h68iipt2c5xd?svg=true
    :target: https://ci.appveyor.com/project/giumas/hyo2-mate
    :alt: AppVeyor Status

.. image:: https://travis-ci.com/hydroffice/hyo2_mate.svg?branch=master
    :target: https://travis-ci.com/hydroffice/hyo2_mate
    :alt: Travis-CI Status

.. image:: https://coveralls.io/repos/github/hydroffice/hyo2_mate/badge.svg?branch=master
    :target: https://coveralls.io/github/hydroffice/hyo2_mate?branch=master
    :alt: coverall

.. image:: https://api.codacy.com/project/badge/Grade/2e5cfbbfcc0b4efdaab2436e11fb0e76
    :target: https://www.codacy.com/app/hydroffice/hyo2_mate
    :alt: Codacy badge

* Code: `GitHub repo <https://github.com/hydroffice/hyo2_mate>`_
* License: Apache 2.0

Installation
------------

Install unit test dependencies::

    pip install pytest pytest-cov

Install QAX dependencies (QA JSON parsing and validation)::

    pip install jsonschema
    pip install appdirs
    pip install --no-deps -e git+https://github.com/hydroffice/hyo2_abc#egg=hyo2.abc
    pip install --no-deps -e git+https://github.com/hydroffice/hyo2_qax#egg=hyo2.qax

Command Line Application
------------------------
Mate includes a simple command line application. Usage can be displayed as follows::

    %> python hyo2/mate/app/cli.py -h

    usage: cli.py [-h] -i INPUT [-o OUTPUT]

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            Path to input QA JSON file
      -o OUTPUT, --output OUTPUT
                            Path to output QA JSON file. If not provided will be
                            printed to stdout.

An example command line is shown below::

    python hyo2/mate/app/cli.py --input tests/test_data/input.json --output tests/test_data/test_out.json


Testing
-------

Unit tests can be run as follows::

    python -m pytest --cov=hyo2.mate --cov-report=html  tests/
