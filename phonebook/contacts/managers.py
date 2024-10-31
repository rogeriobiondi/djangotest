# contacts/managers.py
import requests
from django.conf import settings
from django.db import models

#
# Veja a documentação (CustomManagers):
# https://docs.djangoproject.com/en/5.1/topics/db/managers/
#

class ContactManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()

    def all(self):
        response = requests.get(f"{settings.API_BASE_URL}/contacts/")
        response.raise_for_status()
        data = response.json()
        print("retorno", [self.model(**item) for item in data])
        return [self.model(**item) for item in data]

    def get(self, **kwargs):
        contact_id = kwargs.get('id')
        response = requests.get(f"{settings.API_BASE_URL}/contacts/{contact_id}/")
        response.raise_for_status()
        data = response.json()
        return self.model(**data)

    def create(self, **kwargs):
        response = requests.post(f"{settings.API_BASE_URL}/contacts/", json=kwargs)
        response.raise_for_status()
        data = response.json()
        return self.model(**data)

    def update(self, contact_id, **kwargs):
        response = requests.put(f"{settings.API_BASE_URL}/contacts/{contact_id}/", json=kwargs)
        response.raise_for_status()
        data = response.json()
        return self.model(**data)

    def delete(self, contact_id):
        response = requests.delete(f"{settings.API_BASE_URL}/contacts/{contact_id}/")
        response.raise_for_status()
        return response.status_code == 204