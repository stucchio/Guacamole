from django.db import models
from django.db.models.query import QuerySet
from guacamole.lru import LRUCacheDict


class CachingQuerySet(QuerySet):
    """ This class (designed to be overridden inside _caching_queryset_class) will look up objects in the cache (for some queries, basically just get's)
    rather than hitting SQL for them.
    """
    def __init__(self, *args, **kwargs):
        super(CachingQuerySet, self).__init__(*args, **kwargs)
        self.lookup_query_keywords = ['pk', 'pk__exact', '%s' % self.model._meta.pk.attname, '%s__exact' % self.model._meta.pk.attname]
        self.lookup_query_keywords += self._get_manager().lookup_fields + [ field+"__exact" for field in self._get_manager().lookup_fields]

    def _get_manager(self):
        return self.model.objects

    def _get_lookup_field(self, *args, **kwargs):
        if (len(args) != 0) or (len(kwargs) != 1):
            return None
        for kw in self.lookup_query_keywords:
            if kwargs.has_key(kw):
                return kwargs[kw]
        return None

    def _cache_objects_in_result_cache(self):
        super(CachingQuerySet, self).__len__() #This line might need to change with the implementation
        if hasattr(self, "_result_cache") and self._result_cache and (not hasattr(self, "_saved_result_cache")):
            for obj in self._result_cache:
                for f in self._get_manager().lookup_fields + ['pk']:
                    self._get_manager().cache[getattr(obj, f)] = obj
            self._saved_result_cache = True

    def __len__(self):
        self._cache_objects_in_result_cache()
        return super(CachingQuerySet, self).__len__()

    def get(self, *args, **kwargs):
        lookup_field = self._get_lookup_field(*args, **kwargs)
        if lookup_field: #In this case, we can probably find in the cache
            try:
                return self._get_manager().cache[lookup_field]
            except KeyError:
                result = super(CachingQuerySet, self).get(*args, **kwargs)
                self._get_manager().cache[lookup_field] = result
                return result
        return super(CachingQuerySet, self).get(*args, **kwargs)


def _del_keys(dictionary, keys):
    for k in keys:
        if dictionary.has_key(k):
            del dictionary[k]

class InMemoryCachingManager(models.Manager):
    use_for_related_fields = True #Use this manager even for foreign keys

    def __init__(self, *args, **kwargs):
        self.lookup_fields = kwargs.get('lookup_fields', [])
        self.cache = LRUCacheDict(max_size=kwargs.get("max_size", 1024), expiration=kwargs.get("expiration", 15*60))
        _del_keys(kwargs, ['max_size', 'expiration', 'lookup_fields'] )

        super(InMemoryCachingManager, self).__init__(*args, **kwargs)

    def get_query_set(self):
        return CachingQuerySet(self.model)

    def clear_cache(self):
        self.cache.clear()
