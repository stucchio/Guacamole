"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.db import connection
from django import db
from models import *

import pickle

class SimpleTest(TestCase):
    def setUp(self):
        self.obj = Currency(name="foo")
        self.obj.save()
        self.obj_id = self.obj.id

        regular_obj = Security(name="bar", c=self.obj)
        regular_obj.save()
        self.reg_id = regular_obj.id
        Currency.objects.clear_cache()

        self.many_set = []
        for i in range(20):
            c = Currency(name="many-" + str(i))
            c.save()
            self.many_set.append(c)

    def test_basic_caching(self):
        """
        Test that Currency.objects.get makes no sql query once the object is in cache.
        """
        #1 query will be executed
        self.assertNumQueries(1, lambda: Currency.objects.get(id=self.obj_id) )
        #No queries will be excuted
        self.assertNumQueries(0, lambda: Currency.objects.get(id=self.obj_id) )
        self.assertEqual(self.obj, Currency.objects.get(id=self.obj_id) )

    def test_basic_caching2(self):
        """
        Test that Currency.objects.get makes no sql query once the object is in cache.
        """
        #1 query will be executed
        self.assertNumQueries(1, lambda: Currency.objects.get(pk=self.obj_id) )
        #No queries will be excuted
        self.assertNumQueries(0, lambda: Currency.objects.get(pk=self.obj_id) )
        self.assertEqual(self.obj, Currency.objects.get(pk=self.obj_id) )

    def test_basic_caching3(self):
        """
        Test that Currency.objects.get makes no sql query once the object is in cache.
        """
        #1 query will be executed
        self.assertNumQueries(1, lambda: Currency.objects.get(id=self.obj_id) )
        #No queries will be excuted
        self.assertNumQueries(0, lambda: Currency.objects.get(pk=self.obj_id) )
        self.assertEqual(self.obj, Currency.objects.get(pk=self.obj_id) )

    def test_basic_caching4(self):
        """
        Test that Currency.objects.get makes no sql query once the object is in cache.
        """
        #1 query will be executed
        self.assertNumQueries(1, lambda: Currency.objects.get(id=self.obj_id) )
        #No queries will be excuted
        self.assertNumQueries(0, lambda: Currency.objects.get(name="foo") )
        self.assertEqual(self.obj, Currency.objects.get(name="foo") )

    def test_basic_caching5(self):
        """
        Test that Currency.objects.get raises proper exception if nothing can be found
        """
        #1 query will be executed
        self.assertNumQueries(1, lambda: Currency.objects.get(id=self.obj_id) )
        #No queries will be excuted
        self.assertRaises(Currency.DoesNotExist, lambda: Currency.objects.get(id=self.obj_id, name="nonexistent") )

    def test_caching_many(self):
        self.assertNumQueries(1, lambda: list(Currency.objects.all()) )
        #No queries will be excuted, since object is already in the cache
        self.assertNumQueries(0, lambda: Currency.objects.get(id=self.obj_id) )

    def test_foreign_key_caching(self):
        """
        Test that foreign keys pointing to Currency objects makes no sql query once the object is in cache.
        """
        #1 query will be executed
        reg = Security.objects.get(id=self.reg_id)
        self.assertNumQueries(1, lambda: reg.c )
        #No queries will be excuted
        reg = Security.objects.get(id=self.reg_id) #Get a new Security, since the old one will have the value cached by django's ordinary mechanism
        self.assertNumQueries(0, lambda: reg.c )
        self.assertEqual(reg.c, self.obj)

    def test_regular_not_overridden(self):
        self.assertNumQueries(1, lambda: Security.objects.get(id=self.reg_id) )
        #One query will be excuted, since Security does not use the InMemoryCachingManager
        self.assertNumQueries(1, lambda: Security.objects.get(id=self.reg_id) )

    def test_pickle(self):
        qs = Currency.objects.all()
        unpickled = pickle.loads(pickle.dumps(qs))
        self.assertItemsEqual(qs, unpickled)

