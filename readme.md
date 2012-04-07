# Guacamole

Guacamole is a Django model manager which uses in-memory caching to speed up some queries.

Consider the code:

    class Currency(models.Model):
        name = models.CharField(max_length=256)

    class Security(models.Model):
        name = models.CharField(max_length=256)
        currency = models.ForeignKey(Currency)

With a view:

    def view(request):
        securities = Security.objects.filter(...)[0:50]
	return render_to_response(...)

    <ul>
    {% for security in securities %}
        <li>{{security.name}} (denominated in {{security.currency.name}})</li>
    {% endfor %}
    </ul>

When the view is rendered, there will be 51 SQL queries made - one to retrieve the list of `Securitie`s, and 50 more to retrieve each individual `Currency`. This can be slow - at 1ms of network latency to reach the database, this request will take a minimum of 51ms to return.

One solution is to use `select_related()`, which will condense this down to a single (large) query.

Another solution requires noticing two special properties of currencies - they are virtually immutable and there are very few of them (300-400, maybe?). Thus, it makes a great deal of sense to store them in RAM - they will rarely be out of sync with the database, and they will use up very little memory.

## Usage

With Guacamole, the code could be modified as follows:

    from guacamole import InMemoryCachingManager

    class Currency(models.Model):
        name = models.CharField(max_length=256)

        objects = InMemoryCachingManager()

    class Security(models.Model):
        name = models.CharField(max_length=256)
        currency = models.ForeignKey(Currency)

Whenever a currency foreign key is retrieved via a `get` method, it will be retrieved from an in-memory cache unless it is unavailable.

This is both faster than `select_related` and it is automatic. I.e., if I forget to use `select_related` in some particular view involving `Security`s, it will not cause it to be slow.

### Defaults

The `InMemoryCachingManager` has three settings:

#### lookup_fields

These are the fields of the object which the `InMemoryCachingManager` will use as cache keys. I.e., if we wanted this query to use the cache also:

    Currency.objects.get(name="dollar")

Then you would need to modify the use of the `InMemoryCachingManager` to:

    objects = InMemoryCachingManager(lookup_fields=['name'])

#### max_size

The maximum number of objects to be stored. The least recently used objects will be discarded first. 1024 by default.

#### Expiration

How long objects should remain live. 15 minutes by default.

