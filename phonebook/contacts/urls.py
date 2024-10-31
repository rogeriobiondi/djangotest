# contacts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_list, name='contact_list'),
    path('<int:contact_id>/', views.contact_detail, name='contact_detail'),
]