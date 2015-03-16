:mod:`suseapi.bugzilla`
=======================

.. module:: suseapi.bugzilla
   :synopsis: Bugzilla access library.

.. index:: single: XML

This module allows remote access to Bugzilla. It wraps XML interface to
read Bugzilla and SOAP service for writing to Bugzilla.

.. exception:: BugzillaError

   Base class for all Bugzilla errors.

.. exception:: BugzillaNotPermitted

   Operation was not permitted by Bugzilla.

.. exception:: BugzillaNotFound
   
   Bug was not found.

.. exception:: BugzillaInvalidBugId
   
   Bug ID is invalid.

.. exception:: BugzillaConnectionError

   Failed to connect to bugzilla.

.. exception:: BugzillaLoginFailed

   Login failed.

.. exception:: BuglistTooLarge

   The search result is too long.

.. exception:: BugzillaUpdateError

   Error while updating bugzilla field.

.. class:: Bug(bug_et, anonymous=False)

   :param bug_et: Data obtained from XML interface
   :type bug_et: ElementTree instance

   This class holds all data for single bug from Bugzilla. All XML elements 
   are parsed to the Bug class attributes, so you can access them like 
   ``bug.bug_severity``.

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
   It is subclass of :class:`suseapi.browser.WebScraper`.

   .. method:: login()

      :throws: :exc:`BugzillaLoginFailed` in case login fails.

      Performs login to Bugzilla.
    
   .. method: check_login()

      :rtype: boolean
        
      Check whether we're logged in.

   .. method:: get_bug(bugid, retry=True)

      :param bugid: Bug id
      :type bugid: integer
      :param retry: Whether to retry with new login on failure
      :type retry: boolean
      :return: Bug data
      :rtype: :class:`Bug` instance

      Reads single bug from Bugzilla.

   .. method:: get_bugs(ids, retry=True, permissive=False, store_errors=False)

      :param ids: Bug ids
      :type ids: list of integers
      :param retry: Whether to retry with new login on failure
      :type retry: boolean
      :param permissive: Whether to ignore not found bugs
      :type permissive: boolean
      :param store_errors: Whether to store bug retrieval errors in result
      :type store_errors: boolean
      :return: Bug data
      :rtype: list of :class:`Bug` instances

      Reads list of bugs from Bugzilla.

   .. method:: do_search(params):

      :param params: URL parameters for search
      :type params: list of tuples
      :return: List of bug ids
      :rtype: list of integers
      :throw: :exc:`BuglistTooLarge` in case search result is too long.

      Searches for bugs matching given criteria, you can construct the query
      based on the bugzilla web interface.

   .. method:: get_recent_bugs(startdate)

      :param startdate: Date from which to search.
      :type startdate: datetime instance
      :return: List of bug ids
      :rtype: list of integers
      :throw: :exc:`BuglistTooLarge` in case search result is too long.

      Gets list of bugs modified since defined date.
 
   .. method:: get_openl3_bugs()

      :return: List of bug ids
      :rtype: list of integers
      :throw: :exc:`BuglistTooLarge` in case search result is too long.

      Searches for bugs with openL3 in whiteboard.

   .. method:: get_l3_summary_bugs()

      :return: List of bug ids
      :rtype: list of integers
      :throw: :exc:`BuglistTooLarge` in case search result is too long.

      Searches for open bugs with L3: in summary.

   .. method:: get_sr(bugid)

      :param bugid: Bug id
      :type bugid: integer
      :rtype: list of integers

      Returns list of SRs associated with given bug.
    
   .. method:: update_bug(bugid, callback=None, callback_param=None, whiteboard_add=None, whiteboard_remove=None, \*\*kwargs)

      :param bugid: Bug id
      :type bugid: integer

      Updates single bug in bugzilla.


.. class:: APIBugzilla(user, password, base='https://apibugzilla.novell.com')

    Wrapper around :class:`suseapi.bugzilla.Bugzilla` class to use HTTP
    authentization instead of iChain.

.. class:: DjangoBugzilla(user, password, base='https://apibugzilla.novell.com')

    Wrapper around :class:`suseapi.bugzilla.APIBugzilla` class to use Django
    logging.

.. function:: get_django_bugzilla()

    :rtype: object
    :return: DjangoBugzilla instance

    Constructs :class:`DjangoBugzilla` objects with cookie persistence in
    Django cache, so the there is no need to login on every request.
