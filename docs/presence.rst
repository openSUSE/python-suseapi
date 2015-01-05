:mod:`suseapi.presence`
=======================

.. module:: suseapi.presence
    :synopsis: Presence data library

.. index:: single: Presence


.. class:: Presence(hosts=None)

    :param hosts: List of hosts to query
    :type hosts: list

    Class for querying (and caching) presence data. The optional hosts list can
    define which hosts will be used for querying presence database.
    
    .. method:: get_presence_data(person)

        :param person: Username
        :type person: string
        :rtype: list
        :return: List of absences

        Returns list of absences for given person.
    
    .. method:: is_absent(person, when, threshold=0):

        :param person: Username
        :type person: string
        :param when: Date
        :type when: date
        :param threshold: Threshold for presence check
        :type threshold: integer
        :rtype: bool

        Checks whether person is absent on given date.

        The optional threshold parameter can specify how long absences to
        ignore. For example setting it to 1 will ignore one day absences which
        would otherwise make the method return true.
