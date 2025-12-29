"""
Configuration for fake data generation.
Pydantic models + templates for data generation.

"""
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Gemini model configuration
GEMINI_MODEL = 'gemini-2.5-flash'
GEMINI_TEMPERATURE = 0.7 
GEMINI_MAX_RETRIES = 3


# Number of records to generate for each table
DATA_COUNTS = {
    'genres': 15,
    'labels': 20,
    'users': 10,
    'customers': 100,
    'albums': 200,
    'orders': 150,
    'order_items_per_order': (1, 5),  
    'payments': 150,  
    'shipments': 120,  
    'reviews': 80,
    'cases': 30,
    'case_messages_per_case': (1, 8),  
    'workflows': 10,
    'workflow_executions': 50,
    'integrations': 8,
    'system_logs': 200,
    'inventory_transactions': 300
}


# Template definitions
TEMPLATES = {
        'genre': {
            "name": None
        },
        'label': {
            "name": None
        },
        'customer': {
            "email": None,
            "first_name": None,
            "last_name": None,
            "phone": None
        },
        'album': {
            "title": None,
            "artist": None,
            "genre_id": None,
            "label_id": None,
            "price": None
        },
        'order': {
            "order_number": None,
            "customer_id": None,
            "total": None,
            "shipping_address": None,
            "order_date": None
        },
        'workflow': {
            "name": None,
            "description": None,
            "trigger_type": None,
            "trigger_config": {},
            "workflow_definition": {},
            "enabled": None
        }
    }

# Pydantic Models for validation
class Genre(BaseModel):
    name: str


class Label(BaseModel):
    name: str


class Customer(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str


class Album(BaseModel):
    title: str
    artist: str
    genre_id: str
    label_id: str
    price: float


class Order(BaseModel):
    order_number: str
    customer_id: str
    total: float
    shipping_address: Optional[str] = None
    order_date: str


class Workflow(BaseModel):
    name: str
    description: str
    trigger_type: str
    trigger_config: Dict[str, Any]
    workflow_definition: Dict[str, Any]
    enabled: bool


