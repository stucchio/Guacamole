"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.db import connection
from django import db
from models import *


class SimpleTest(TestCase):
    def setUp(self):
        self.obj = CachedModel(name="foo")
        self.obj.save()
        self.obj_id = self.obj.id

        regular_obj = RegularModel(name="bar", c=self.obj)
        regular_obj.save()
        self.reg_id = regular_obj.id
        CachedModel.objects.clear_cache()

    def test_basic_caching(self):
        """
        Test that CachedModel.objects.get makes no sql query once the object is in cache.
        """
        #1 query will be executed
        self.assertNumQueries(1, lambda: CachedModel.objects.get(id=self.obj_id) )
        #No queries will be excuted
        self.assertNumQueries(0, lambda: CachedModel.objects.get(id=self.obj_id) )
        self.assertEqual(self.obj, CachedModel.objects.get(id=self.obj_id) )

    def test_foreign_key_caching(self):
        """
        Test that foreign keys pointing to CachedModel objects makes no sql query once the object is in cache.
        """
        #1 query will be executed
        reg = RegularModel.objects.get(id=self.reg_id)
        self.assertNumQueries(1, lambda: reg.c )
        #No queries will be excuted
        reg = RegularModel.objects.get(id=self.reg_id)
        self.assertNumQueries(0, lambda: reg.c )
        self.assertEqual(reg.c, self.obj)



