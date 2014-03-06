Examples
========

Bugzilla
--------

Getting single bug from bugzilla::

    from suseapi.bugzilla import Bugzilla
    bugzilla = Bugzilla('user', 'pass')
    bug = bugzilla.get_bug(123456)

Searching for bugs changed in last hour::

    from suseapi.bugzilla import Bugzilla
    bugzilla = Bugzilla('user', 'pass')
    bugs = bugzilla.bugzilla.do_search([
        ('chfieldfrom', '1h'),
    ])
