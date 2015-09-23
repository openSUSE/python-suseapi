SUSEAPI command line interface
==============================

.. program:: suseapi

Synopsis
++++++++

.. code-block:: text

    suseapi <command> [options]

Commands actually indicate which operation should be performed.

Description
+++++++++++

This module also installs :program:`suseapi` program, which allows you to
easily access some of the functionality from command line. Currently following
subcommands are available:

.. option:: lookup-user [--by BY] [--attribs ATTRIBS] value

    Lookups user information using :mod:`suseapi.userinfo`.

.. option:: absence value

    Lookups user absence information using :mod:`suseapi.presence`.

Files
+++++

~/.config/suseapi
    User configuration file
/etc/xdg/suseapi
    Global configration file

The program follows XDG specification, so you can adjust placement of config files 
by environment variables ``XDG_CONFIG_HOME`` or ``XDG_CONFIG_DIRS``.

The configuration file is INI file, for example:

.. code-block:: ini

    [ldap]
    server = ldap://pan.suse.de
    base = o=Novell

    [presence]
    servers = present.suse.de,bolzano.suse.de/nosend

Examples
++++++++

Listing absences for user mcihar:

.. code-block:: sh

    $ suseapi absence mcihar
    2015-04-06 - 2015-04-06
    2015-05-01 - 2015-05-01
    2015-05-08 - 2015-05-08
    2015-07-06 - 2015-07-06
    2015-09-28 - 2015-09-28
    2015-10-28 - 2015-10-28

Listing LDAP attributes for user mcihar:

.. code-block:: sh

    $ suseapi lookup-user --attribs COMPANY,FULLNAME,uid mcihar
    [('cn=MCihar,o=Novell',
      {'COMPANY': ['SUSE'], 'FULLNAME': ['Michal Cihar'], 'uid': ['mcihar']})]
