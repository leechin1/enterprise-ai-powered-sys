# Function Calling Tools Reference

This document provides comprehensive documentation for all 26 LangChain function calling tools available to the AI Business Intelligence System.

## The AI Issues Agent - Main Feature

The AI Issues Agent is the primary intelligence system of this platform, providing autonomous business issue detection and resolution. It uses a sophisticated multi-stage pipeline:

1. **SQL Generation (Stage 0)** - AI analyzes database schema and generates targeted SQL queries
2. **Issue Identification (Stage 1)** - Query results are analyzed to identify critical business issues
3. **Fix Proposals (Stage 2)** - Automated fix proposals with pre-generated emails

The agent supports domain-focused analysis (inventory, payments, customers, revenue) and operates in two modes:
- **Classic Mode** - Three-stage UI with step-by-step analysis
- **Conversational Mode** - Multi-turn ReAct agent dialogue

## Overview

Tools are organized into categories:

| Category | Module | Tool Count | Purpose |
|----------|--------|------------|---------|
| **Query Tools** | `query_tools.py` | 11 | Read-only analytics and data retrieval |
| **Generation Tools** | `generation_tools.py` | 4 | Content generation and write operations |
| **Issues Query Tools** | `issues_query_tools.py` | 2 | SQL generation and execution |
| **Issues Analysis Tools** | `issues_analysis_tools.py` | 4 | Issue identification and lookup |
| **Issues Fix Tools** | `issues_fix_tools.py` | 4 | Fix proposals and email sending |
| **Issues Utility Tools** | `issues_utility_tools.py` | 2 | State management |

**Total: 26 Tools**

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

---

## Issues Agent Tools

The Issues Agent uses a separate set of tools for autonomous business issue detection and resolution. These tools work in a sequential pipeline with shared state management.

### Tool Categories

| Category | Module | Purpose |
|----------|--------|---------|
| **Query Tools** | `issues_query_tools.py` | SQL generation and execution |
| **Analysis Tools** | `issues_analysis_tools.py` | Issue identification and lookup |
| **Fix Tools** | `issues_fix_tools.py` | Fix proposals and email sending |
| **Utility Tools** | `issues_utility_tools.py` | State management |

### State Management

All Issues Agent tools share state through `IssuesAgentState` singleton:
- `queries`: Generated SQL queries
- `query_results`: Executed query results
- `issues`: Identified business issues
- `proposed_fixes`: Generated fix proposals
- `focus_areas`: Areas being analyzed

---

### Query Tools

#### `generate_business_queries`

Generates SQL queries to investigate potential business issues. This is typically the **FIRST step** in the analysis pipeline.

**Purpose:** Creates targeted SQL queries based on focus areas to gather data for issue analysis.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `focus_areas` | `str` | `"all"` | Areas to focus analysis on |

**Focus Area Options:**
- `"inventory"` - Stock issues
- `"payments"` - Payment/transaction issues
- `"customers"` - Customer satisfaction issues
- `"revenue"` - Sales/revenue concerns
- `"operations"` - Operational issues
- `"all"` - Comprehensive analysis (default)
- Can combine multiple: `"inventory, payments"`

**Returns:** `str` - Summary of generated queries with purposes and priorities

**Example Output:**
```
✅ **Generated 5 SQL Queries**
Focus areas: inventory, payments

1. 🔴 **Find out-of-stock items** (critical)
   _Identifies albums with zero inventory_

2. 🟠 **Check failed payments** (high)
   _Retrieves all failed payment transactions_

**Next step:** Call `execute_business_queries()` to run these queries.
```

---

#### `execute_business_queries`

Executes the previously generated SQL queries against the database.

**Purpose:** Runs all generated queries and stores results for analysis.

**Parameters:** None

**Prerequisites:** Must call `generate_business_queries()` first

**Returns:** `str` - Summary of query execution with row counts

**Example Output:**
```
✅ **Executed 5/5 Queries Successfully**

✅ **Find out-of-stock items**: 3 rows
✅ **Check failed payments**: 7 rows
✅ **Low stock items**: 12 rows

**Next step:** Call `analyze_issues_from_results()` to identify business issues.
```

---

### Analysis Tools

#### `analyze_issues_from_results`

Analyzes query results to identify business issues using AI.

**Purpose:** Uses LLM to interpret query data and identify actionable business problems.

**Parameters:** None

**Prerequisites:** Must call `execute_business_queries()` first

**Returns:** `str` - Detailed list of identified issues with severity and descriptions

**Severity Levels:**
- 🔴 `critical` - Requires immediate attention
- 🟠 `high` - Should be addressed soon
- 🟡 `medium` - Should be monitored
- 🟢 `low` - Minor concern

**Category Icons:**
- 📦 `inventory` - Stock-related issues
- 💳 `payments` - Payment/transaction issues
- 👥 `customers` - Customer satisfaction
- 💰 `revenue` - Sales/revenue issues
- ⚙️ `operations` - Operational issues
- 📊 `data_quality` - Data integrity issues

**Example Output:**
```
⚠️ **Identified 3 Business Issues**

### 1. 📦 Critical Stock Shortage
**Severity:** 🔴 CRITICAL | **Category:** inventory

5 albums are completely out of stock with pending customer orders.

---

### 2. 💳 Failed Payment Spike
**Severity:** 🟠 HIGH | **Category:** payments

7 payment failures in the last 24 hours, up 300% from normal.

---

**Next step:** Call `propose_fix_for_issue(issue_number)` to get a fix proposal.
```

---

#### `get_issue_details`

Gets detailed information about a specific identified issue.

**Purpose:** Retrieve full details for a single issue without re-running analysis.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `issue_number` | `int` | Yes | The issue number (1-based index) |

**Returns:** `str` - Full details including severity, category, description, and affected records

---

#### `get_issue_detail`

Alias for `get_issue_details` - identical functionality.

---

#### `find_issue_by_keyword`

Search for issues by keyword in title or description.

**Purpose:** Find issues when you know part of the name but not the number.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `keyword` | `str` | Yes | Word or phrase to search for |

**Returns:** `str` - Matching issue details, or list of all issues if no match

**Example Output (multiple matches):**
```
🔍 **Found 2 issues matching 'payment':**

2. 🟠 **Failed Payment Spike**
5. 🟡 **Payment Method Distribution Imbalance**

Call `get_issue_details(N)` to see full details for a specific issue.
```

---

### Fix Tools

#### `propose_fix_for_issue`

Generates a detailed fix proposal for a specific issue, including automated actions and email notifications.

**Purpose:** Creates actionable fix plans with recipient lists and pre-generated emails.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `issue_number` | `int` | Yes | The issue number (1-based) from identified issues |

**Prerequisites:** Must call `analyze_issues_from_results()` first

**Returns:** `str` - Comprehensive fix proposal including:
- Fix title and description
- Automated actions to take
- Expected outcome
- Priority level
- List of recipients with roles and contact info
- Pre-generated email previews

**Example Output:**
```
## 🔧 Fix Proposal for Issue #1

**Issue:** Critical Stock Shortage

### Urgent Inventory Restock Required
_Immediate reorder of out-of-stock albums with pending orders_

### 📋 Automated Actions
- Flag affected orders for customer notification
- Generate purchase orders for suppliers
- Update inventory status in system

**Expected Outcome:** Stock replenished within 3-5 business days
**Priority:** IMMEDIATE

### 👥 Recipients (2)
- **Sarah Chen** (inventory_manager)
  Email: sarah@company.com | Reason: Manages supplier relationships
- **Mike Johnson** (operations_lead)
  Email: mike@company.com | Reason: Oversees fulfillment

### 📧 Emails Ready to Send (2)

**Email 1:** Urgent: Immediate Restock Required
To: sarah@company.com
```
Dear Sarah,

We have identified 5 albums that are out of stock...
```

---
**Next steps:**
- Call `send_fix_emails()` to send the notification emails
- Call `edit_email(email_number, field, new_value)` to modify an email first
```

---

#### `generate_email_for_issue`

Generates an email on-demand for a specific issue using templates from `tools_templates/`.

**Purpose:** Create notification emails for issues that don't have pre-generated emails from fix proposals, or when you need a different type of email.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `issue_number` | `int` | Required | The issue number (1-based) from identified issues |
| `email_type` | `str` | `"management"` | Type of notification email to generate |

**Email Types:**

| Type | Template | Recipient | Use Case |
|------|----------|-----------|----------|
| `"management"` | `management_notification_template.txt` | hi@mistyrecords.com | Alert leadership about business issues |
| `"supplier"` | `supplier_notification_template.txt` | hi@mistyrecords.com | Contact suppliers about inventory/stock |
| `"customer"` | `customer_notification_template.txt` | hi@mistyrecords.com | Notify customers about issues affecting them |
| `"team"` | `team_notification_template.txt` | hi@mistyrecords.com | Alert internal team members |

**Note:** ALL email types use `hi@mistyrecords.com` as the hardcoded recipient. The EmailService routes to the actual destination (placebo email in test mode, hi@mistyrecords.com in production).

**Prerequisites:** Must call `analyze_issues_from_results()` first to have identified issues

**Returns:** `str` - Generated email preview with subject, recipient, and body

**Example Output:**
```
## 📧 Email Generated for Issue #3

**Type:** Management Notification
**Subject:** [HIGH] Business Issue Alert: Widespread Overstocking
**To:** hi@mistyrecords.com

**Preview:**
```
Dear Management Team,

This is an automated notification regarding a HIGH priority business issue.

Issue: Widespread Overstocking
Severity: HIGH
Category: Inventory

Description:
25 albums have stock levels exceeding 100 units with low sales velocity...

Please review and take appropriate action.

Best regards,
Misty Jazz Records Business Intelligence System
```

✅ **Email ready to send!**
```

**Note:** After generating an email, it is stored in state and can be sent using `send_fix_emails()` or edited using `edit_email()`.

---

#### `edit_email`

Edit a specific field of a generated email before sending.

**Purpose:** Allows modification of auto-generated emails for accuracy or tone.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `email_number` | `int` | Yes | Which email to edit (1-based index) |
| `field` | `str` | Yes | Field to edit: `"subject"` or `"body"` |
| `new_value` | `str` | Yes | The new value for the field |

**Prerequisites:** Must call `propose_fix_for_issue()` first

**Returns:** `str` - Confirmation with updated email preview

**Example Output:**
```
✅ **Email 1 Updated**

**Field:** subject
**Old value:** Urgent: Immediate Restock Required
**New value:** ACTION REQUIRED: Critical Stock Shortage

**Updated Email Preview:**
Subject: ACTION REQUIRED: Critical Stock Shortage
To: sarah@company.com
```
Dear Sarah,

We have identified 5 albums...
```
```

---

#### `send_fix_emails`

Sends all notification emails for the currently proposed fix.

**Purpose:** Dispatches emails to all recipients. In placebo mode, all emails go to the test address.

**Parameters:** None

**Prerequisites:** Must call `propose_fix_for_issue()` first

**Email Routing:**
- **Placebo Mode:** All emails sent to `PLACEBO_EMAIL` with `[PLACEBO: original@email.com]` in subject
- **Production Mode:** All external emails routed to `DEFAULT_EXTERNAL_EMAIL` (hi@mistyrecords.com) with intended recipient in subject

**Returns:** `str` - Confirmation with sent/failed counts

**Example Output:**
```
## 📬 Email Results

**Sent:** 2 ✅
**Failed:** 0

🧪 **Placebo Mode Active**
All emails were sent to: `test@company.com`

### Emails Sent:
1. **ACTION REQUIRED: Critical Stock Shortage**
   Intended for: sarah@company.com
2. **Inventory Alert: Immediate Action Needed**
   Intended for: mike@company.com

✅ **Fix execution complete!**
```

---

### Utility Tools

#### `get_current_analysis_state`

Gets a summary of the current analysis pipeline state.

**Purpose:** Check what has been done so far in the analysis workflow.

**Parameters:** None

**Returns:** `str` - State summary showing completed steps

**Example Output:**
```
## 📊 Current Analysis State

**Queries Generated:** 5 ✅
**Queries Executed:** 5 results ✅
**Issues Identified:** 3 ✅
  1. [CRITICAL] Critical Stock Shortage
  2. [HIGH] Failed Payment Spike
  3. [MEDIUM] Customer Review Decline
**Fix Proposed:** Yes ✅ (for issue #1)

**Focus Areas:** inventory, payments
```

---

#### `reset_analysis`

Resets all analysis state to start fresh.

**Purpose:** Clear all stored data to begin a new analysis session.

**Parameters:** None

**Returns:** `str` - Confirmation message

**Example Output:**
```
🔄 **Analysis state reset!**

Ready to start a new analysis. You can:
- Call `generate_business_queries()` to investigate all areas
- Call `generate_business_queries('inventory')` to focus on specific areas
```

---

## Issues Agent Workflow

The recommended workflow for the Issues Agent:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ISSUES AGENT PIPELINE                        │
└─────────────────────────────────────────────────────────────────┘

1. generate_business_queries("focus_areas")
         │
         ▼
2. execute_business_queries()
         │
         ▼
3. analyze_issues_from_results()
         │
         ├──► get_issue_details(N)      [Optional: view details]
         ├──► find_issue_by_keyword()   [Optional: search issues]
         │
         ▼
4. propose_fix_for_issue(issue_number)
         │                    OR
         ├──► generate_email_for_issue(N, type)  [On-demand email]
         │
         ├──► edit_email(N, field, value)  [Optional: modify]
         │
         ▼
5. send_fix_emails()

         ▼
   [reset_analysis() to start over]
```

---

## Tool Integration

### LangChain Usage

All Issues Agent tools are exposed as function wrappers:

```python
from services.tools import (
    # Query tools
    generate_business_queries,
    execute_business_queries,
    # Analysis tools
    analyze_issues_from_results,
    get_issue_details,
    get_issue_detail,
    find_issue_by_keyword,
    # Fix tools
    propose_fix_for_issue,
    generate_email_for_issue,  # On-demand email generation
    edit_email,
    send_fix_emails,
    # Utility tools
    get_current_analysis_state,
    reset_analysis,
)
```
