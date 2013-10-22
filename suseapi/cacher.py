from datetime import datetime, timedelta


class CacherMixin(object):
    '''
    Generic cacher mixin using object attribute.
    '''
    _cache = {}

    def _cache_set(self, key, value):
        '''
        Remembers value in internal cache.
        '''
        self._cache[key] = (value, datetime.now())

    def _cache_uptodate(self, key):
        '''
        Checks whether cache entry is valid.
        '''
        return (self._cache[key][1] + timedelta(days=1)) > datetime.now()

    def _cache_get(self, key, force=False):
        '''
        Gets value from internal cache.
        '''
        if key in self._cache and (force or self._cache_uptodate(key)):
            return self._cache[key][0]
        return None


class DjangoCacherMixin(CacherMixin):
    '''
    Cacher mixin using Django.
    '''
    cache_key = 'cache-%s'

    def _cache_key(self, key):
        '''
        Get name of the cache key for django caching.
        '''
        return self.cache_key % key

    def _cache_set(self, key, value):
        '''
        Sets value in django cache.
        '''
        from django.core.cache import cache
        cache.set(self._cache_key(key), value, 24 * 3600)

    def _cache_get(self, key, force=False):
        '''
        Gets value from django cache.
        '''
        from django.core.cache import cache
        return cache.get(self._cache_key(key))
