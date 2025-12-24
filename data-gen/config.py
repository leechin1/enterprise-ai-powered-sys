"""
Configuration for fake data generation
"""

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

# Gemini model configuration
GEMINI_MODEL = 'gemini-2.5-flash'
GEMINI_TEMPERATURE = 0.7 
GEMINI_MAX_RETRIES = 3

