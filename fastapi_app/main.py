# fastapi_app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import UUID, uuid4

app = FastAPI()

class Contact(BaseModel):
    id: UUID
    first_name: str
    last_name: str = None
    phone_number: str
    email: str = None
    address: str = None
    city: str = None
    state: str = None
    zip_code: str = None
    created_at: str
    updated_at: str

# Mocked data
contacts = [
    Contact(
        id=uuid4(), 
        first_name="John", 
        last_name="Doe", 
        phone_number="1234567890", 
        email="john.doe@example.com", 
        address="123 Main St",
        city="Springfield",
        state="IL",
        zip_code="62701",
        created_at="2024-10-18 17:47:20.581084+00:00",
        updated_at="2024-10-18 17:47:20.581084+00:00"        
    ),
    Contact(
        id=uuid4(), 
        first_name="Jane", 
        last_name="Doe", 
        phone_number="0987654321", 
        email="jane.doe@example.com", 
        address="456 Elm St",
        city="Springfield",
        state="IL",
        zip_code="62701",
        created_at="2024-10-18 17:47:20.581084+00:00",
        updated_at="2024-10-18 17:47:20.581084+00:00"
    ),
]

@app.get("/contacts/", response_model=List[Contact])
async def get_contacts():
    return contacts

@app.get("/contacts/{contact_id}", response_model=Contact)
async def get_contact(contact_id: UUID):
    for contact in contacts:
        if contact.id == contact_id:
            return contact
    raise HTTPException(status_code=404, detail="Contact not found")

@app.post("/contacts/", response_model=Contact)
async def create_contact(contact: Contact):
    contact.id = uuid4()
    contacts.append(contact)
    return contact