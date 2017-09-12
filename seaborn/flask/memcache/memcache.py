"""
    This is wrapper around a MemCache functional.

    Currently this is implemented with a simple dictionary but later it can be ported to use the
    real MemCache library.
"""
from datetime import datetime, timedelta
from seaborn.logger import SeabornLogger
log = SeabornLogger()


class MemCache():
    def __init__(self):
        self.cache = {}

    def get(self, key_base, request_parameters, html_format=False):
        """
            This will get a cache results to make requests faster
        :param key_base:            str of base name to store the key under usually this will be the endpoint url
        :param request_parameters:  dict of parameters that can be substituted into key_template
        :param html_format:         bool of true if return format is html
        :return:                    tuple of the cache_key and result (result will be None if there is no cache)
        """
        try:
            cache_key = key_base if html_format else "html_"+key_base
            bypass = request_parameters.pop('bypass_cache', False)

            if request_parameters:
                cache_key += ' '+' '.join([str(value) for key, value in sorted(request_parameters.items())])

            if bypass:
                return cache_key, None

            if cache_key not in self.cache:
                return cache_key, None

            lifetime, value = self.cache[cache_key]
            if lifetime is not None and lifetime < datetime.utcnow():
                self.delete(cache_key)
                return cache_key, None

            if html_format:
                return cache_key, value
            else:
                return cache_key, (value, 200, {'Content-Type':'application/json'})
        except Exception as ex:
            log.exception("Exception in MemCache.get: %s"%ex)
            return None, None

    def set(self, cache_key, value, cache_hours=None, cache_lifetime=None):
        """
            This will get a cache results to make requests faster
        :param cache_key:      str of the key to store the value under
        :param cache_hours:    float of the number of hours to store the cache results, default is use cache_lifetime
        :param cache_lifetime: datetime of when to delete the results, default is no limit
        :return:               None
        """
        try:
            if cache_key is None:
                return
            if cache_hours is not None:
                cache_lifetime = datetime.utcnow()+ timedelta(hours=cache_hours)
            self.cache[cache_key] = (cache_lifetime, value)
        except Exception as ex:
            log.exception("Exception in MemCache.set: %s"%ex)

    def delete(self, key_template, request_parameters=None):
        """
        :param key_template:       str of key template with %(arg)s for parameter replacement
        :param request_parameters: dict of values to substitute
        :return:                   None
        """
        try:
            if request_parameters is not None:
                cache_key = key_template % request_parameters
            else:
                cache_key = key_template

            self.cache.pop(cache_key, None)
        except Exception as ex:
            log.exception("Exception in MemCache.delete: %s"%ex)