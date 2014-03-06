:mod:`suseapi.srinfo`
=====================


.. module:: suseapi.srinfo
    :synopsis: SR information retrieval

.. index:: single: SR

This module allows remote access to SR database.

.. class:: SRInfo()

    .. method:: get_status(srid)

        :param srid: SR id
        :type srid: integer
        :rtype: string
        :return: String with status

        Returns SR status.

    .. method:: get_info(srid)

        :param srid: SR id
        :type srid: integer
        :rtype: dict 
        :return: Dictionary with SR attributes

        Returns SR status.

.. class:: DjangoSRInfo()

    Wrapper around :class:`suseapi.srinfo.SRInfo` class to use Django settings and cache
    results in Django cache.
