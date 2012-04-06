from django.db import models
from guacamole.lru import LRUCacheDict


class InMemoryCachingManager(models.Manager):
    use_for_related_fields = True

    def __init__(self, *args, **kwargs):
        max_size = kwargs.get("max_size", 1024)
        expiration = kwargs.get("expiration", 15*60)
        self.__cache = LRUCacheDict(max_size, expiration)
        super(InMemoryCachingManager, self).__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        print (args, kwargs)
        if kwargs.has_key('id'):
            pk_id = kwargs['id']
            try:
                return self.__cache[pk_id]
            except KeyError:
                result = super(InMemoryCachingManager, self).get(*args, **kwargs)
                self.__cache[pk_id] = result
                return result
        return super(InMemoryCachingManager, self).get(*args, **kwargs)

