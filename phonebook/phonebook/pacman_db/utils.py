import django 

# Hard copy from psycopg2
from datetime import date, time

error_codes_DUPLICATE_DATABASE = '42P04'


class Inet(object):
    def __init__(self, addr):
        self.addr = addr

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.addr)

    def prepare(self, conn):
        self._conn = conn

    def getquoted(self):
        obj = self.addr
        if hasattr(obj, 'prepare'):
            obj.prepare(self._conn)
        return obj.getquoted() + b"::inet"

    def __str__(self):
        return str(self.addr)


def quote_postgre(value):
    if type(value) == bool:
        return str(value).lower()
    if type(value) == date:
        return "'{}'::date".format(value)
    if type(value) == time:
        return "'{}'::time".format(value)
    if '@' in str(value):
        return "'{}'".format(value)
    if type(value) == int or type(value) == float:
        if value < 0:  # Why exactly?
            return ' {}'.format(value)
        return value
    return "'{}'".format(value)


def split_identifier(identifier):
    """
    Split a SQL identifier into a two element tuple of (namespace, name).
    The identifier could be a table, column, or sequence name might be prefixed
    by a namespace.
    """
    try:
        from django.db.backends.utils import \
            split_identifier as django_split_identifier
        return django_split_identifier(identifier)
    except ImportError:
        try:
            namespace, name = identifier.split('"."')
        except ValueError:
            namespace, name = '', identifier
        return namespace.strip('"'), name.strip('"')


def is_django_2():
    return django.VERSION[0] == 2


def is_django_1():
    return django.VERSION[0] == 1


def is_string(obj):
    if isinstance(obj, str):
        return True

    try:
        return isinstance(obj, unicode)
    except NameError:  # Python3
        return isinstance(obj, bytes)
    return False