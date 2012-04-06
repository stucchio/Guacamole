from django.db import models
from django.db.models.query import QuerySet
from guacamole.lru import LRUCacheDict


def _caching_queryset_class(mgr):
    class CachingQuerySet(QuerySet):
        manager = mgr
        def __init__(self, *args, **kwargs):
            super(CachingQuerySet, self).__init__(*args, **kwargs)
            self.lookup_query_keywords = ['pk', 'pk__exact', '%s' % self.model._meta.pk.attname, '%s__exact' % self.model._meta.pk.attname]
            self.lookup_query_keywords += self.manager.lookup_fields + [ field+"__exact" for field in self.manager.lookup_fields]

        def __get_lookup_field(self, *args, **kwargs):
            for kw in self.lookup_query_keywords:
                if kwargs.has_key(kw):
                    return kwargs[kw]
            return None

        def get(self, *args, **kwargs):
            lookup_field = self.__get_lookup_field(*args, **kwargs)
            try:
                return self.manager.cache[lookup_field]
            except KeyError:
                result = super(CachingQuerySet, self).get(*args, **kwargs)
                self.manager.cache[lookup_field] = result
                return result
            return super(CachingQuerySet, self).get(*args, **kwargs)

    return CachingQuerySet

class InMemoryCachingManager(models.Manager):
    use_for_related_fields = True

    def __init__(self, *args, **kwargs):
        self.lookup_fields = kwargs.get("lookup_fields", [])
        self.cache = LRUCacheDict(max_size=kwargs.get("max_size", 1024), expiration=kwargs.get("expiration", 15*60))

        self.queryset_class = _caching_queryset_class(self)

        super(InMemoryCachingManager, self).__init__(*args, **kwargs)

    def get_query_set(self):
        return self.queryset_class(self.model)

    def get(self, *args, **kwargs):
        for field in self.lookup_fields:
            if kwargs.has_key(field):
                pk_id = kwargs[field]
                try:
                    return self.cache[pk_id]
                except KeyError:
                    result = super(InMemoryCachingManager, self).get(*args, **kwargs)
                    self.cache[pk_id] = result
                return result
        return super(InMemoryCachingManager, self).get(*args, **kwargs)

    def clear_cache(self):
        self.cache.clear()
