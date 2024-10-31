# phonebook/custom_database/pacman_database/query.py

from django.db.models.query import QuerySet
import requests

# from contacts import models
from django.db import models

class PacmanQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model=model, query=query, using=using, hints=hints)
        self.api_url = "http://" + self._db.settings_dict['HOST'] + \
                        ":" +  self._db.settings_dict['PORT']
        print(f"PacmanDB: Connection to {self.api_url}...")

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(self._iterable_class(self))
        return self._result_cache

    def iterator(self):
        print(f"Pacman DB: Querying {self.api_url}/{self.query}...")
        response = requests.get(f"{self.api_url}/{self.query}")
        response.raise_for_status()
        results = response.json()
        for result in results:
            yield self.model(**result)

class PacmanManager(models.Manager):
    def get_queryset(self):
        return PacmanQuerySet(self.model, using=self._db)