============
Storing data
============

.. py:currentmodule:: htables

Database
--------
Several database backends are supported with `htables`. The most natural
is PostgreSQL because it has a native `hstore` column type. SQLite is
also supported, and it's useful when running unit tests, because
setup, teardown, and operations on small amounts of data are much faster
with SQLite, especially if the database is in-memory.


Session pool
------------
We instantiate a DB object to connect to a database, passing in a
connection string. We actually have a session pool at this point. It's a
good idea to activate `debug` mode if the application is running in
development or unit test mode. This will make sure that we don't save
integers or other non-string values in the database.

::

    >>> database = htables.SqliteDB(':memory:', debug=True)


Session
-------
To actually read and write data we need a :class:`Session`. It's a proxy to
access :class:`Table` objects, blob files, and handles transactions. The
session pool gives out session objects and collects them back when we're
done. Be aware that :meth:`~PostgresqlDB.put_session` aborts the current
transaction.

::

    >>> session = database.get_session()
    >>> try:
    ...     # do some stuff
    ...     session.commit()
    ... except:
    ...     session.rollback()
    ... finally:
    ...     database.put_session()


Table
-----
Tables are collections of rows. They are in fact SQL tables with a
simple schema: an integer auto-incremented unique `id`, and a `data`
column. The :meth:`~Table.create_table` and :meth:`~Table.drop_table`
methods are available on the :class:`Table` object::

    >>> person_table = session['person']
    >>> person_table.create_table()

Tables also have methods for creating and fetching rows.
:meth:`~Table.new` creates a record, :meth:`~Table.find` fetches all
matching records, :meth:`~Table.find_first` and
:meth:`~Table.find_single` are useful when we only need to get one
record, and :meth:`~Table.get` fetches a record based on its `id`::

    >>> person = person_table.new(name="Joe")
    >>> person.id
    1
    >>> people = list(person_table.find())
    >>> first_person = person_table.find_first()
    >>> joe = person.find_single(name="Joe")
    >>> joe
    {u'name': u'Joe'}
    >>> joe = person_table.get(1)


:meth:`~Table.find` performs equality comparison for its keyword
arguments and returns an iterator over all matching rows. The
convenience methods :meth:`~Table.find_first` and
:meth:`~Table.find_single` return a single row. If no row is found they
raise a :class:`~Table.RowNotFound` exception. Additionally, with
:meth:`~Table.find_single`, if several rows match the query, it raises a
:class:`~Table.MultipleRowsFound` exception. The exceptions are
conveniently aliased on the :class:`Table` object.


Row
---
A :class:`Row` represents a record in a table. It has a unique integer
`id` that is generated by the database backend, there is no support for
custom `id` values. Rows are never instantiated directly; they are
obtained via methods of :class:`Table`.

The :class:`Row` object is a Python `dict` whose keys and values are
restricted to unicode strings. This restriction is enforced at
:meth:`~Row.save` time if the database was opened with ``debug=True``.
The database backend may also refuse to store non-string values.

Rows are created by calling :meth:`Table.new()` which takes the same
arguments as the Python `dict` constructor. This method will actually
save the row in the database in order to generate its `id`. The returned
row object is identical to a row returned by the :meth:`Table.find`
methods. After changing a row, call its :meth:`~Row.save` method to
write it to the database. :meth:`~Row.delete` removes the row. All
changes are written in a transaction so they only become permanent after
calling :meth:`Session.commit()`.

::

    >>> person['name']
    u'Joe'
    >>> person['email'] = 'joe@example.com'
    >>> person.update({'some': 'more', 'data': ''})
    >>> person.save()


.. note::
   Any changes to :class:`Row` objects are only made in Python memory.
   They are written to the database (pending transaction commit) when
   calling :meth:`Row.save()`. This means that any unsaved changes are
   not reflected in calls to :meth:`Table.find()`, it will just return
   new copies of the old rows from the database.
