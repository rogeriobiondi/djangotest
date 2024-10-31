import requests

class Cursor(object):

    def __init__(self, connection):
        self.connection = connection
        self.api_url = f"http://{connection.settings_dict['HOST']}:{connection.settings_dict['PORT']}"

    def execute(self, query, vars=None):
        # http://initd.org/psycopg/docs/cursor.html#cursor.query
        self.query = query.encode('utf-8')
        response = requests.get(f"{self.api_url}/{query}", params=vars)
        response.raise_for_status()
        self.results = response.json()

    def close(self, *args, **kwargs):
        pass

    def fetchone(self, *args, **kwargs):
        # return None
        return self.results[0] if self.results else None

    def fetchmany(self, *args, **kwargs):
        return []

    def fetchall(self, *args, **kwargs):
        # return []
        return self.results
