:mod:`suseapi.browser`
=======================

.. module:: suseapi.browser
   :synopsis: Web browser emulation class

.. index:: single: HTML

This module wraps :mod:`mechanize` module to provide higher level of
abstraction for our needs.

.. exception:: WebScraperError

   Base class for all web scaper errors.

.. class:: WebScraper(user, password, base, useragent=None)

    .. method:: request(action, paramlist=None, \*\*kwargs)

        Performs single request.

    .. method:: set_cookies(cookies)

        Sets browser cookies.

    .. method:: get_cookies()

        Returns list of current browser cookies.
