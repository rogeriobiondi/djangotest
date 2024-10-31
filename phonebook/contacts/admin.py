from django.contrib import admin

from phonebook import settings

from .query import ListQuerySet

# Register your models here.
from .models import Contact

from unittest.mock import Mock, MagicMock
from django.db.models import QuerySet


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')

    def get_queryset(self, request):        
        if settings.FS_CONTACT_SOURCE == "api":
            print("AQQQQ", Contact.objects.all())
            listquery = ListQuerySet(
                list_data = Contact.objects.all(), model=Contact)
            # queryset = QuerySet(model=Contact, using=listquery.db)
            # queryset._result_cache = list(listquery)
            return listquery # queryset
        else:
            return super().get_queryset(request).all()
        
