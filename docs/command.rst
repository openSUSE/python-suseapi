Command line interface
======================

.. program:: suseapi

This module also installs :program:`suseapi` program, which allows you to
easily access some of the functionality from command line. Currently following
subcommands are available:

.. option:: lookup-user [--by BY] value

    Lookups user information using :mod:`suseapi.userinfo`.

.. option:: absence value

    Lookups user absence information using :mod:`suseapi.presence`.
