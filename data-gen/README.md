# Fake Data Generator for Misty AI Enterprise System

This folder contains a data generation system that uses Google's Gemini API to generate realistic fake data for your database.

## Features

- Uses Gemini AI to generate contextually realistic data
- Generates data for all database tables
- Respects foreign key relationships
- Configurable data counts
- Direct database insertion via Supabase

## Setup

### 1. Install Dependencies

```bash
cd data-gen
pip install -r requirements.txt
```

### 2. Environment Variables

Make sure your `.env` file in the parent directory contains:

```
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_secret_key
```

The `GEMINI_API_KEY` is already configured in your `.env` file.

### 3. Database Setup

Before running the data generator, ensure your database schema is set up by running the migration scripts:

```bash
# From the parent directory
psql your_database_url < db_configure/migrations/01_core_tables.sql
psql your_database_url < db_configure/migrations/02_workflow_tables.sql
psql your_database_url < db_configure/migrations/03_indexes.sql
psql your_database_url < db_configure/migrations/04_rls_policies.sql
```

Or use Supabase's SQL editor to run each migration file.

## Usage

### Generate Data

Run the main script to generate and insert fake data:

```bash
python generate_data.py
```

The script will:
1. Connect to your Supabase database (you'll be prompted for the password)
2. Generate realistic fake data using Gemini API
3. Insert data in the correct order (respecting foreign keys)
4. Display progress for each table

### Configuration

Edit `config.py` to customize:

- **Data counts**: Number of records to generate for each table
- **Gemini settings**: Model, temperature, retry attempts
- **Relationships**: Min/max values for related records (e.g., items per order)

Example configuration:

```python
DATA_COUNTS = {
    'customers': 100,      # Generate 100 customers
    'albums': 200,         # Generate 200 albums
    'orders': 150,         # Generate 150 orders
    # ... more tables
}
```

## Data Generated

The system generates data for the following tables:

### Core Tables (01_core_tables.sql)
- ✅ genres
- ✅ labels
- ✅ users
- ✅ customers
- ✅ albums
- ✅ inventory
- ✅ inventory_transactions
- ✅ orders
- ✅ order_items
- ✅ payments
- ✅ shipments
- ✅ reviews

### Workflow Tables (02_workflow_tables.sql)
- ✅ cases
- ✅ case_messages
- ✅ workflows
- ✅ workflow_executions
- ✅ system_logs
- ✅ integrations

## How It Works

### 1. Gemini Generator (`gemini_generator.py`)

Uses Google's Gemini API to generate realistic data based on detailed prompts. For example:

- **Customers**: Realistic names, emails, addresses, purchase history
- **Albums**: Jazz album titles, artists, realistic SKUs, pricing
- **Cases**: Customer service scenarios with AI sentiment analysis
- **Workflows**: Business automation configurations

### 2. Database Connector (`db_connector.py`)

Handles:
- Database connection to Supabase PostgreSQL
- Bulk data insertion using `psycopg2`
- Returns generated UUIDs for foreign key relationships
- Transaction management and error handling

### 3. Main Script (`generate_data.py`)

Orchestrates the entire process:
- Generates data in dependency order
- Handles relationships between tables
- Creates synthetic data for complex scenarios (order items, payments, etc.)
- Provides progress feedback

## Database Connection

The script will prompt you for your Supabase database password when it runs. You can find your connection details in:

1. Supabase Dashboard → Settings → Database
2. Copy the connection string (Transaction Mode)
3. Enter the password when prompted

Alternatively, you can modify `db_connector.py` to use environment variables for the password.

## Example Output

```
============================================================
FAKE DATA GENERATION WITH GEMINI API
============================================================

DATABASE CONNECTION SETUP
...
Enter your Supabase database password: ****
✓ Connected to database successfully

1. Generating genres...
✓ Generated 15 records
✓ Inserted 15 genres

2. Generating labels...
✓ Generated 20 records
✓ Inserted 20 labels

...

============================================================
✓ DATA GENERATION COMPLETED SUCCESSFULLY!
============================================================
```

## Troubleshooting

### Connection Issues

If you have trouble connecting to Supabase:
- Verify your `SUPABASE_URL` in `.env`
- Ensure your IP is allowed in Supabase dashboard (Database → Settings → Connection Pooling)
- Try using the direct connection string from Supabase

### Gemini API Issues

If data generation fails:
- Verify your `GEMINI_API_KEY` is valid
- Check your API quota at [Google AI Studio](https://makersuite.google.com/)
- The script has automatic retry logic (3 attempts)

### Data Quality

The AI-generated data should be realistic but may occasionally have:
- Minor inconsistencies
- Duplicate values (retry if this happens)

The script includes validation and error handling to minimize these issues.

## Customization

### Add Custom Prompts

Edit `gemini_generator.py` to modify prompts for more specific data:

```python
def generate_customers(self, count: int) -> List[Dict]:
    prompt = """
    Your custom prompt here...
    """
    return self.generate_data(prompt, count)
```

### Add New Tables

1. Add to `config.py`:
   ```python
   DATA_COUNTS = {
       'your_table': 50,
   }
   ```

2. Add generator method in `gemini_generator.py`
3. Add insert method in `db_connector.py`
4. Call in `generate_data.py` in the correct dependency order

## License

Part of the Misty AI Enterprise System
