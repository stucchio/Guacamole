from django.db import models
from django.db.models.query import QuerySet
from guacamole.lru import LRUCacheDict


class _CachingQuerySet(QuerySet):
    """ This class (designed to be overridden inside _caching_queryset_class) will look up objects in the cache (for some queries, basically just get's)
    rather than hitting SQL for them.
    """
    def __init__(self, *args, **kwargs):
        super(_CachingQuerySet, self).__init__(*args, **kwargs)
        self.lookup_query_keywords = ['pk', 'pk__exact', '%s' % self.model._meta.pk.attname, '%s__exact' % self.model._meta.pk.attname]
        self.lookup_query_keywords += self.manager.lookup_fields + [ field+"__exact" for field in self.manager.lookup_fields]

    def _get_lookup_field(self, *args, **kwargs):
        if (len(args) != 0) or (len(kwargs) != 1):
            return None
        for kw in self.lookup_query_keywords:
            if kwargs.has_key(kw):
                return kwargs[kw]
        return None

    def _cache_objects_in_result_cache(self):
        super(_CachingQuerySet, self).__len__() #This line might need to change with the implementation
        if hasattr(self, "_result_cache") and self._result_cache and (not hasattr(self, "_saved_result_cache")):
            for obj in self._result_cache:
                for f in self.manager.lookup_fields + ['pk']:
                    self.manager.cache[getattr(obj, f)] = obj
            self._saved_result_cache = True

    def __len__(self):
        self._cache_objects_in_result_cache()
        return super(_CachingQuerySet, self).__len__()

    def get(self, *args, **kwargs):
        lookup_field = self._get_lookup_field(*args, **kwargs)
        if lookup_field: #In this case, we can probably find in the cache
            try:
                return self.manager.cache[lookup_field]
            except KeyError:
                result = super(_CachingQuerySet, self).get(*args, **kwargs)
                self.manager.cache[lookup_field] = result
                return result
        return super(_CachingQuerySet, self).get(*args, **kwargs)


def _caching_queryset_class(mgr):
    class CustomCachingQueryset(_CachingQuerySet):
        manager = mgr
    return CustomCachingQueryset

class InMemoryCachingManager(models.Manager):
    use_for_related_fields = True #Use this manager even for foreign keys

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('lookup_fields'):
            self.lookup_fields = kwargs["lookup_fields"]
            del kwargs['lookup_fields']
        else:
            self.lookup_fields = []

        self.cache = LRUCacheDict(max_size=kwargs.get("max_size", 1024), expiration=kwargs.get("expiration", 15*60))
        self.queryset_class = _caching_queryset_class(self)
        super(InMemoryCachingManager, self).__init__(*args, **kwargs)

    def get_query_set(self):
        return self.queryset_class(self.model)

    def clear_cache(self):
        self.cache.clear()
