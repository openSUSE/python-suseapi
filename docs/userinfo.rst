:mod:`suseapi.userinfo`
=======================

.. module:: suseapi.userinfo
    :synopsis: LDAP access library.

.. index:: single: LDAP

This module allows remote access to LDAP. It wraps standard Python module for
LDAP and provides some convenience functions.

.. class:: UserInfo(server, base)

   :param server: Server address
   :type server: string
   :param base: Search base
   :type base: string

   LDAP class wrapping ldap access.

   .. method:: search_uid(uid, attribs=None)

      :param uid: Search string
      :type uid: string
      :param attribs: Attributes to read from LDAP, defaults to ['cn', 'mail', 'ou', 'sn', 'givenName']
      :type attribs: list of strings
      :rtype: list of dictionaries
      :return: Search results

      Performs UID search and returns list of search results.

   .. method:: search_by(attr, val, attribs=None)

      :param attr: attribute name to search by
      :param val: value of the attribute to search for
      :param attribs: attributes to return

      Performs search by any attribute.

   .. method:: get_department(user)

      :param user: Search string
      :type user: string
      :rtype: string
      :return: Department name, ``N/A`` in case it was not found.

      Performs LDAP search and grabs department name from it. Additionally
      some fixups are applied to department names to avoid more names for
      single department.

.. class:: DjangoUserInfo(server, base)

    Wrapper around :class:`suseapi.userinfo.UserInfo` class to use Django settings and cache
    results in Django cache.
