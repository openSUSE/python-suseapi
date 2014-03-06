:mod:`suseapi.browser`
======================

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

        :param cookies: Cookies to set
        :type cookies: List of strings

        Sets authentication cookies. 

    .. method:: get_cookies()

        :return: Authentication cookies
        :rtype: List of strings

        Gets list of authentication cookies. 
