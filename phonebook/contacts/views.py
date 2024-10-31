from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Contact #, PacmanContact

# Create your views here.


def contact_list(request):
    contacts = Contact.objects.all()
    # contacts = PacmanContact.objects.all()
    # contacts = Contact.objects.using('pacman').all()
    return render(request, 'contacts/contact_list.html', {'contacts': contacts})

def contact_detail(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    return render(request, 'contacts/contact_detail.html', {'contact': contact})