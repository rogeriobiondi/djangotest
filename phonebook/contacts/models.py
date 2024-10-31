# contacts/models.py
from django.db import models


from phonebook.settings import FS_CONTACT_SOURCE

# Usar o Custom Manager no Modelo
from .managers import ContactManager

# Usar um Custom Database
from phonebook.pacman_db.query import PacmanManager

class Contact(models.Model):
    # id uuid NOT NULL PRIMARY KEY,
    id = models.UUIDField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=16)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Contact Manager - Feature Switch
    if FS_CONTACT_SOURCE == "api":
        objects = ContactManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

# class PacmanContact(models.Model): 
#     id = models.UUIDField(primary_key=True)
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50, blank=True, null=True)
#     phone_number = models.CharField(max_length=16)
#     email = models.EmailField(blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     city = models.CharField(max_length=50, blank=True, null=True)
#     state = models.CharField(max_length=50, blank=True, null=True)
#     zip_code = models.CharField(max_length=10, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     objects = PacmanManager()

#     def __str__(self):
#         return f"{self.first_name} {self.last_name or ''}".strip()
    
#     class Meta:
#         managed = False
#         db_table = 'contacts'