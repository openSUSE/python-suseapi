:mod:`suseapi.swamp`
====================

.. module:: suseapi.swamp
   :synopsis: SWAMP access library.

.. index:: single: SOAP
           single: suds

This module allows remote access to :index:`SWAMP` service. It is basically just a
wrapper around suds to workaround some weirdness which SWAMP :index:`SOAP` interface
exposes.


.. class:: SWAMP(user, password, url=None, tracefile=None)

    :param user: User name.
    :type user: string
    :param password: Password to authenticate to SWAMP.
    :type password: string
    :param url: SWAMP URL (default is http://swamp.suse.de:8080/axis/services/swamp)
    :type url: string
    :param tracefile: File handle where SOAP traces will be written.
    :type tracefile: file object


    .. method:: getMethodDoc(name)

        Gets online documentation for method.

        :param name: Name of method
        :type name: string

        :return: Documentation for method
        :rtype: string

    .. method:: getAllDocs()

        Gets online documentation for all methods.

        :return: Documentation for all methods
        :rtype: dict

    .. method:: login()

        Logins to SWAMP.

        This actually only tests whether login information is correct.

        :return: None

    .. method:: doGetProperty(name)

        Gets SWAMP property.

        :param name: Name of property
        :type name: string

        :return: Value of property
        :rtype: string

    .. method:: getWorkflowInfo(id)

        Gets the workflows properties.

        :param id: Workflow ID.
        :type id: integer

        :return: Workflow properties.

    .. method:: doGetAllDataPaths(id)

        Gets all workflows data paths.

        :param id: Workflow ID.
        :type id: integer

        :return: Workflow data paths.

    .. method:: doGetData(id, path)

        Gets workflow data bit.

        :param id: Workflow ID.
        :type id: integer
        :param path: Data path.
        :type path: string

        :return: Workflow data bit value.

    .. method:: doGetAllData(id)

        Gets all workflow data bits.

        :param id: Workflow ID.
        :type id: integer

        :return: Workflow data bit values.
        :rtype: dict

    .. method:: getDataBit(id, path)

        Efficient wrapper around :meth:`doGetAllData` and :meth:`doGetData` to
        get a data bit.  It first tries to use all data, because getting it
        takes same time as single bit, but the data is cached and reused for
        next time.

        :param id: Workflow ID.
        :type id: integer
        :param path: Data path.
        :type path: string

        :return: Workflow data bit value.
        :rtype: string

    .. method:: doSendData(id, path, value)

        Sets data bit in a workflow.

        :param id: Workflow ID.
        :type id: integer
        :param path: Data path.
        :type path: string
        :param value: Data value.
        :type value: string

        :return: None

    .. method:: doSendEvent(id, envent)

        Sets data bit in a workflow.

        :param id: Workflow ID.
        :type id: integer
        :param event: Event name.
        :type event: string

        :return: None
