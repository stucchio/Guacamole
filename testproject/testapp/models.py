from django.db import models
from guacamole import InMemoryCachingManager

class Currency(models.Model):
    name = models.CharField(max_length=256)

    objects = InMemoryCachingManager(lookup_fields=['name'])

    def __unicode__(self):
        return self.name

class Security(models.Model):
    name = models.CharField(max_length=256)
    c = models.ForeignKey(Currency)

    def __unicode__(self):
        return self.name
