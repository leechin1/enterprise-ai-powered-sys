"""
Pydantic models + templates for data generation.
"""
from pydantic import BaseModel, ValidationError, Field
from typing import List, Dict, Any, Optional


# Template definitions
TEMPLATES = {
        'genre': {
            "name": None,
            "description": None,
            "avg_margin": None,
            "popularity_score": None
        },
        'label': {
            "name": None,
            "country": None,
            "founded_year": None
        },
        'user': {
            "email": None,
            "first_name": None,
            "last_name": None,
            "role": None
        },
        'customer': {
            "email": None,
            "first_name": None,
            "last_name": None,
            "phone": None,
            "address": None,
            "date_joined": None,
            "lifetime_value": None,
            "total_purchases": None,
            "preferred_genre": None,
            "status": None
        },
        'album': {
            "sku": None,
            "title": None,
            "artist": None,
            "genre_id": None,
            "label_id": None,
            "release_year": None,
            "price": None,
            "cost": None,
            "condition": None,
            "description": None,
            "is_rare": None,
            "estimated_value": None
        },
        'order': {
            "order_number": None,
            "customer_id": None,
            "subtotal": None,
            "tax": None,
            "shipping_fee": None,
            "total": None,
            "status": None,
            "channel": None,
            "shipping_address": None,
            "order_date": None
        },
        'case': {
            "customer_id": None,
            "subject": None,
            "description": None,
            "category": None,
            "priority": None,
            "status": None,
            "assigned_to": None,
            "ai_sentiment": None,
            "ai_score": None,
            "ai_suggestion": None,
            "resolution_notes": None,
            "created_at": None,
            "resolved_at": None
        },
        'workflow': {
            "name": None,
            "description": None,
            "trigger_type": None,
            "trigger_config": {},
            "workflow_definition": {},
            "enabled": None
        },
        'integration': {
            "service_name": None,
            "category": None,
            "connected": None,
            "settings": {},
            "sync_frequency": None,
            "error_count": None,
            "last_error": None
        },
        'system_log': {
            "log_level": None,
            "source": None,
            "message": None,
            "metadata": {},
            "user_id": None,
            "created_at": None
        }
    }

# Pydantic Models for validation
class Genre(BaseModel):
    name: str
    description: str
    avg_margin: float = Field(ge=25.0, le=45.0)
    popularity_score: int = Field(ge=50, le=100)


class Label(BaseModel):
    name: str
    country: str
    founded_year: int = Field(ge=1940, le=2020)


class User(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: str


class Customer(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str
    address: str
    date_joined: str
    lifetime_value: float
    total_purchases: int
    preferred_genre: Optional[str] = None
    status: str


class Album(BaseModel):
    sku: str
    title: str
    artist: str
    genre_id: str
    label_id: str
    release_year: int
    price: float
    cost: float
    condition: str
    description: str
    is_rare: bool
    estimated_value: Optional[float] = None


class Order(BaseModel):
    order_number: str
    customer_id: str
    subtotal: float
    tax: float
    shipping_fee: float
    total: float
    status: str
    channel: str
    shipping_address: Optional[str] = None
    order_date: str


class Case(BaseModel):
    customer_id: str
    subject: str
    description: str
    category: str
    priority: str
    status: str
    assigned_to: Optional[str] = None
    ai_sentiment: str
    ai_score: int
    ai_suggestion: str
    resolution_notes: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None


class Workflow(BaseModel):
    name: str
    description: str
    trigger_type: str
    trigger_config: Dict[str, Any]
    workflow_definition: Dict[str, Any]
    enabled: bool


class Integration(BaseModel):
    service_name: str
    category: str
    connected: bool
    settings: Dict[str, Any]
    sync_frequency: str
    error_count: int
    last_error: Optional[str] = None


class SystemLog(BaseModel):
    log_level: str
    source: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    created_at: str
