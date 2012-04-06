from django.db import models
from guacamole import InMemoryCachingManager

class CachedModel(models.Model):
    name = models.CharField(max_length=256)

    objects = InMemoryCachingManager()

    def __unicode__(self):
        return self.name

class RegularModel(models.Model):
    name = models.CharField(max_length=256)
    c = models.ForeignKey(CachedModel)


    def __unicode__(self):
        return self.name
