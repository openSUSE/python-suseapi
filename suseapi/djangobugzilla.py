'''
Helper functions for write access to Bugzilla.
'''
from django.core.cache import cache
from django.conf import settings
import traceback
from suseapi.bugzilla import APIBugzilla


class DjangoBugzilla(APIBugzilla):
    '''
    Adds Django specific things to bugzilla class.
    '''
    def _log_parse_error(self, bugid, data):
        '''
        Sends email to admin on error.
        '''
        from django.core.mail import mail_admins
        subject = 'Error while fetching %s' % bugid
        message = 'Exception:\n\n%s\n\n\nData:\n\n%s\n' % (
            traceback.format_exc(),
            data,
        )
        mail_admins(subject, message, fail_silently=True)
        super(DjangoBugzilla, self).log_parse_error(bugid, data)


def get_bugzilla():
    '''
    Returns logged in bugzilla object. Access cookies are stored in django
    cache.
    '''
    bugzilla = DjangoBugzilla(
        settings.BUGZILLA_USERNAME,
        settings.BUGZILLA_PASSWORD,
        useragent=settings.EMAIL_SUBJECT_PREFIX.strip('[] '),
        timeout=settings.BUGZILLA_TIMEOUT
    )

    # Check for anonymous access
    if settings.BUGZILLA_USERNAME == '':
        return bugzilla

    cookies = cache.get('bugzilla-access-cookies')

    if cookies is None:
        bugzilla.login()
        cache.set('bugzilla-access-cookies', bugzilla.get_cookies())
    else:
        bugzilla.set_cookies(cookies)

    return bugzilla
