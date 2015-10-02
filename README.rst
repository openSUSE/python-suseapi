python-suseapi
==============

.. image:: https://travis-ci.org/openSUSE/python-suseapi.png?branch=master   
    :alt: Build status
    :target: https://travis-ci.org/openSUSE/python-suseapi

.. image:: https://coveralls.io/repos/openSUSE/python-suseapi/badge.svg?branch=master&service=github
    :alt: Code coverage
    :target: https://coveralls.io/github/openSUSE/python-suseapi?branch=master

.. image:: https://landscape.io/github/openSUSE/python-suseapi/master/landscape.png
    :alt: Code Health
    :target: https://landscape.io/github/openSUSE/python-suseapi/master

.. image:: http://img.shields.io/pypi/dm/python-suseapi.svg
    :alt: PyPi
    :target: https://pypi.python.org/pypi/python-suseapi

.. image:: https://api.codacy.com/project/badge/3976586fadbe46458063d432cd72a02e
    :alt: Codacy Badge
    :target: https://www.codacy.com/public/michal_2/python-suseapi

Python module to work with various SUSE services. Please note that many of them
are internal only.

Documentation is available at http://python-suseapi.readthedocs.org/.

Bugzilla
--------

Simple interface for Novell bugzilla, allowing to download, search or
manipulate with bugs. It relies on web scraping using mechanize for many
tasks.

Maintained data
---------------

Process database of maintained data. This will be soon obsolete as this
information should be in Build Service.

Presence
--------

Access to vacation and holiday information.

Products
--------

Basic mapping of various variants of product name to standard notation.

Service request information
---------------------------

Retrieval information about service requests.

SWAMP
-----

Module for interfacing SWAMP using SOAP interface based on suds library.
