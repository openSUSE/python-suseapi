:mod:`suseapi.bugzilla`
====================

.. module:: suseapi.bugzilla
   :synopsis: Bugzilla access library.

.. index:: single: SOAP
           single: XML

This module allows remote access to Bugzilla. It wraps XML interface to
read Bugzilla and SOAP service for writing to Bugzilla.

.. exception:: WebScraperError

   Base class for all web scaper errors.

.. exception:: BugzillaError

   Base class for all Bugzilla errors.

.. exception:: BugzillaNotPermitted

   Operation was not permitted by Bugzilla.

.. exception:: BugzillaNotFound
   
   Bug was not found.

.. exception:: BugzillaLoginFailed

   Login failed.

.. exception:: BuglistTooLarge

   The search result is too long.

.. exception:: URLError

   URL error while talking to Bugzilla.

.. exception:: BugzillaUpdateError

   Error while updating bugzilla field.

.. class:: Bug(et)

   :param et: Data obtained from XML interface
   :type et: ElementTree instance

   This class holds all data for single bug from Bugzilla.

.. class:: Bugzilla(user, password, base='https://bugzilla.novell.com')

   :param user: Username to Bugzilla
   :type user: string
   :param password: Password to Bugzilla
   :type password: string
   :param base: Base URL for Bugzilla
   :type base: string

   Bugzilla communication class for read only access. With iChain
   authentication. The authentication part is expensive so it is good idea to
   remember authentication cookies and reuse them as much as possible.

   .. method:: set_cookies(cookies)

      :param cookies: Cookies to set
      :type cookies: List of strings

      Sets authentication cookies. 

   .. method:: get_cookies()

      :return: Authentication cookies
      :rtype: List of strings

      Gets list of authentication cookies. 

   .. method:: login()

      :throws: :exc:`BugzillaLoginFailed` in case login fails.

      Performs login to Bugzilla.

   .. method:: get_bug(id, retry=True)

      :param id: Bug id
      :type id: integer
      :param retry: Whether to retry with new login on failure
      :type retry: boolean
      :return: Bug data
      :rtype: :class:`Bug` instance

      Reads single bug from Bugzilla.

   .. method:: get_bugs(ids, retry=True)

      :param ids: Bug ids
      :type ids: list of integers
      :param retry: Whether to retry with new login on failure
      :type retry: boolean
      :return: Bug data
      :rtype: list of :class:`Bug` instances

      Reads list of bugs from Bugzilla.

   .. method:: get_recent_bugs(startdate)

      :param startdate: Date from which to search.
      :type startdate: datetime instance
      :return: List of bug ids
      :rtype: list of integers
      :throw: :exc:`BuglistTooLarge` in case search result is too long.

      Gets list of bugs modified since defined date.


.. function:: update_bug(user, cookie, bugid, updates, url=BUGZILLA_SOAP_URL)
    
    :param user: Email of user which should be used as author of changes. If
        the email is not existing in Bugzilla, the update will not happen and you
        will not get any failure.
    :type user: string
    :param cookie: Authentication cookie, which is secret string used to
        access SOAP intefrace.
    :type cookie: string
    :param bugid: Bug to update
    :type bugid: integer
    :param updates: Updates to the bug. Please note that interface allows to
        enter more updates at once, but in most cases such request fails. See
        :func:`get_bug_update_xml` for description of this parameter.
    :type updates: dictionary
    :param url: Bugzilla SOAP interface URL.
    :type url: string
    :throw: :exc:`BugzillaUpdateError` in case of failure

    
    Updates bug using SOAP interface.

.. function:: get_bug_update_xml(updates)

    :param updates: Updates to the bug.
    :type updates: dictionary

    Generates XML to update bug. This function should not be used directly and
    is called internally from :func:`update_bug`.

    The update dictionary keys are fields to update, following fields are
    currently supported
    
        * keywords (extended)
        * cc (extended)
        * comment (with private flag)
        * product
        * component
        * status
        * resolution
        * assignee
        * qa_contact
        * url
        * summary
        * status_whiteboard
        * hardware
        * os
        * found_in_version
        * priority
        * severity
        * target_milestone
        * original_estimate
        * deadline
        * partner_id
        * found_by
        * business_priority
        * services_priority
        * nts_support_number

    The fields which have no comment allow only to replace whole value of the
    field and expect new value to be stored in dictionary.

    The comment field allows to specify private flag for a comment, so you can
    specify value either as string (no private flag will be set) or as a
    tuple, where second member is a boolean indicating private flag.

    The extended fields (keywords and cc currently) allow finer grained
    control - you can add/delete parts or replace whole value. In this case
    function expects tuple, where first member is action to perform (``add``,
    ``delete`` or ``replace``) and second member is the value.
