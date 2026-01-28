# Function Calling Tools Reference

This document provides comprehensive documentation for all LangChain function calling tools available to the AI Business Consultant Agent.

## Overview

Tools are organized into two categories:

| Category | Module | Purpose |
|----------|--------|---------|
| **Query Tools** | `business_query_tools.py` | Read-only analytics and data retrieval |
| **Generation Tools** | `business_generation_tools.py` | Content generation and write operations |

---

## Query Tools (Read-Only)

These tools retrieve and analyze business data without modifying the database.

### `scan_business_metrics`

Scans and retrieves all key business metrics from the database.

**Purpose:** Provides a comprehensive snapshot of business health across financial, customer, inventory, and payment dimensions.

**Parameters:** None

**Returns:** `str` - Formatted summary containing:
- Financial metrics (total revenue, total orders, average order value)
- Customer metrics (total customers, average rating, total reviews)
- Inventory metrics (total items, total value, low stock count, out of stock)
- Payment status summary (completed, pending, failed counts)

**Example Output:**
```
BUSINESS METRICS SUMMARY:

FINANCIAL:
- Total Revenue: $125,000.00
- Total Orders: 450
- Average Order Value: $277.78

CUSTOMERS:
- Total Customers: 200
- Average Rating: 4.35/5.0
- Total Reviews: 180

INVENTORY:
- Total Items: 500
- Total Value: $75,000.00
- Low Stock Items (≤10): 12
- Out of Stock: 3

PAYMENTS:
- Completed: 420
- Pending: 25
- Failed: 5
```

---

### `get_top_performing_products`

Retrieves top-selling albums ranked by revenue and units sold.

**Purpose:** Identifies best-performing products for inventory and marketing decisions.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | `int` | `5` | Number of top products to retrieve |

**Returns:** `str` - Formatted list of top albums with:
- Album title and artist
- Units sold
- Total revenue generated

**Example Output:**
```
TOP 5 PERFORMING PRODUCTS:

1. 'Kind of Blue' by Miles Davis
   - Units Sold: 45
   - Revenue: $1,350.00

2. 'A Love Supreme' by John Coltrane
   - Units Sold: 38
   - Revenue: $1,140.00
```

---

### `get_top_customers`

Retrieves top customers ranked by total spending.

**Purpose:** Identifies high-value customers for loyalty programs and targeted marketing.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | `int` | `5` | Number of top customers to retrieve |

**Returns:** `str` - Formatted list of customers with:
- Customer name
- Total amount spent
- Number of orders

**Example Output:**
```
TOP 5 CUSTOMERS BY SPENDING:

1. John Smith
   - Total Spent: $2,500.00
   - Orders: 12

2. Jane Doe
   - Total Spent: $1,800.00
   - Orders: 8
```

---

### `get_low_stock_items`

Retrieves albums with inventory levels below the specified threshold.

**Purpose:** Identifies items requiring restock to prevent stockouts.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `threshold` | `int` | `10` | Stock level threshold (items at or below this level are returned) |

**Returns:** `str` - Formatted list of low stock items with:
- Album title and artist
- Current stock quantity
- Album ID (for restock operations)

**Example Output:**
```
LOW STOCK ITEMS (≤10 units):

1. 'Blue Train' by John Coltrane
   - Current Stock: 3 units
   - Album ID: abc123-def456

2. 'Maiden Voyage' by Herbie Hancock
   - Current Stock: 5 units
   - Album ID: ghi789-jkl012
```

---

### `get_failed_payments`

Retrieves all payment transactions with failed status.

**Purpose:** Identifies payment issues requiring attention or customer follow-up.

**Parameters:** None

**Returns:** `str` - Formatted list of failed payments with:
- Payment ID
- Associated order ID
- Amount
- Payment method
- Transaction ID

**Example Output:**
```
FAILED PAYMENTS:

1. Payment ID: pay_abc123
   - Order ID: ord_xyz789
   - Amount: $150.00
   - Method: credit_card
   - Transaction ID: txn_failed_001
```

---

### `get_pending_payments`

Retrieves all payment transactions with pending status.

**Purpose:** Monitors outstanding payments awaiting processing or confirmation.

**Parameters:** None

**Returns:** `str` - Formatted list of pending payments with:
- Payment ID
- Associated order ID
- Amount
- Payment method

---

### `get_genre_performance`

Retrieves sales performance metrics aggregated by music genre.

**Purpose:** Analyzes which genres drive the most revenue for inventory planning.

**Parameters:** None

**Returns:** `str` - Formatted list of genres with:
- Genre name
- Units sold
- Total revenue

**Example Output:**
```
GENRE PERFORMANCE:

1. Bebop
   - Units Sold: 120
   - Revenue: $3,600.00

2. Modal Jazz
   - Units Sold: 95
   - Revenue: $2,850.00
```

---

### `get_label_performance`

Retrieves sales performance metrics aggregated by record label.

**Purpose:** Identifies top-performing labels for purchasing and partnership decisions.

**Parameters:** None

**Returns:** `str` - Formatted list of labels with:
- Label name
- Units sold
- Total revenue

---

### `get_top_rated_albums`

Retrieves highest-rated albums based on customer reviews.

**Purpose:** Identifies quality inventory for recommendations and marketing.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | `int` | `5` | Number of top-rated albums to retrieve |

**Returns:** `str` - Formatted list of albums with:
- Album title and artist
- Average rating (out of 5.0)
- Number of reviews

**Example Output:**
```
TOP 5 RATED ALBUMS:

1. 'Time Out' by Dave Brubeck
   - Average Rating: 4.85/5.0
   - Review Count: 22

2. 'Speak No Evil' by Wayne Shorter
   - Average Rating: 4.75/5.0
   - Review Count: 18
```

---

### `get_payment_method_distribution`

Retrieves distribution of payment methods used by customers.

**Purpose:** Analyzes payment preferences for checkout optimization.

**Parameters:** None

**Returns:** `str` - Formatted list of payment methods with:
- Payment method name
- Transaction count
- Total amount processed

**Example Output:**
```
PAYMENT METHOD DISTRIBUTION:

1. Credit Card
   - Transaction Count: 280
   - Total Amount: $84,000.00

2. Paypal
   - Transaction Count: 120
   - Total Amount: $36,000.00
```

---

### `get_revenue_by_date`

Retrieves daily revenue breakdown.

**Purpose:** Analyzes sales trends over time for forecasting and planning.

**Parameters:** None

**Returns:** `str` - Formatted daily breakdown with:
- Date
- Revenue amount
- Order count

**Example Output:**
```
DAILY REVENUE BREAKDOWN:

2025-01-15: $2,500.00 (8 orders)
2025-01-16: $3,200.00 (12 orders)
2025-01-17: $1,800.00 (6 orders)
```

---

## Generation Tools (Write Operations)

These tools generate content and perform database modifications.

### `generate_customer_email`

Generates a personalized email template for a specific customer.

**Purpose:** Creates customer communications for notifications, promotions, and follow-ups.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `customer_id` | `str` | Yes | Customer UUID |
| `email_type` | `str` | Yes | Type of email (e.g., `low_stock_notification`, `thank_you`, `promotion`) |
| `context` | `str` | Yes | Additional context/body content for the email |

**Returns:** `str` - Formatted email template with:
- Recipient email address
- Subject line (derived from email_type)
- Personalized greeting
- Context content
- Signature

**Example Output:**
```
EMAIL TEMPLATE GENERATED
========================

To: customer@email.com
Subject: Thank You - Misty Jazz Records

Dear John Smith,

Thank you for your recent purchase of 'Kind of Blue'. We hope you enjoy this classic album!

Best regards,
Misty Jazz Records Team

========================
Note: This is a generated template. Review before sending.
```

---

### `generate_inventory_alert_email`

Generates an inventory alert email for low stock items.

**Purpose:** Creates alerts for inventory managers to initiate restocking.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `album_ids` | `str` | Yes | Comma-separated list of album IDs with low stock |

**Returns:** `str` - Formatted inventory alert email with:
- Recipient (inventory manager)
- Alert subject line
- List of low stock items with quantities
- Action request

**Example Output:**
```
INVENTORY ALERT EMAIL
=====================

To: inventory@mistyjazzrecords.com
Subject: LOW STOCK ALERT - Immediate Action Required

Dear Inventory Manager,

The following items have critically low stock levels and require immediate reordering:

1. 'Blue Train' by John Coltrane - 3 units remaining
2. 'Maiden Voyage' by Herbie Hancock - 5 units remaining

Please review and place restock orders as soon as possible to avoid stockouts.

Best regards,
Misty AI Business Intelligence System
=====================
```

---

### `cancel_transaction`

Cancels a pending or failed payment transaction.

**Purpose:** Handles payment cancellation for problematic transactions.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `payment_id` | `str` | Yes | Payment UUID to cancel |
| `reason` | `str` | Yes | Reason for cancellation |

**Returns:** `str` - Confirmation message with:
- Payment ID
- Order ID
- Amount
- Previous status
- New status (cancelled)
- Cancellation reason

**Constraints:**
- Cannot cancel payments with `completed` status (requires refund process instead)
- Updates payment status to `cancelled` in database

**Example Output:**
```
TRANSACTION CANCELLED
====================
Payment ID: pay_abc123
Order ID: ord_xyz789
Amount: $150.00
Previous Status: failed
New Status: cancelled
Reason: Customer requested cancellation due to duplicate order
====================
```

---

### `recommend_restock_quantity`

Recommends optimal restock quantity for an album based on sales history.

**Purpose:** Provides data-driven restocking recommendations to optimize inventory.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `album_id` | `str` | Yes | Album UUID |

**Returns:** `str` - Recommendation with:
- Album title and artist
- Current stock level
- Total units sold historically
- Recommended restock quantity
- Rationale for recommendation

**Recommendation Logic:**
| Total Sold | Recommended Qty | Rationale |
|------------|-----------------|-----------|
| > 50 units | 100 units | High demand item |
| > 20 units | 50 units | Moderate demand |
| ≤ 20 units | 25 units | Standard restock |

**Example Output:**
```
RESTOCK RECOMMENDATION
======================
Album: 'Kind of Blue' by Miles Davis
Current Stock: 5 units
Total Sold: 65 units
Recommended Restock: 100 units
Rationale: High demand item
======================
```

---

## Tool Integration

### LangChain Usage

All tools are exposed as function wrappers for LangChain integration:

```python
from services.tools import (
    # Query tools (read-only)
    scan_business_metrics,
    get_top_performing_products,
    get_top_customers,
    get_low_stock_items,
    get_failed_payments,
    get_pending_payments,
    get_genre_performance,
    get_label_performance,
    get_top_rated_albums,
    get_payment_method_distribution,
    get_revenue_by_date,
    # Generation tools (write operations)
    generate_customer_email,
    generate_inventory_alert_email,
    cancel_transaction,
    recommend_restock_quantity,
)
```

### Error Handling

All tools return error messages in the format:
```
Error [operation]: [error message]
```

Tools gracefully handle:
- Database connection failures
- Missing records (customer/album not found)
- Empty result sets
- Invalid parameters
