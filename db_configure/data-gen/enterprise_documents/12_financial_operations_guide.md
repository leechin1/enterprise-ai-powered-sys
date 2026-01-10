# Misty Jazz Records - Financial Operations Guide

## Internal Financial Procedures

**Confidential - Management Use Only**

---

## Chart of Accounts

### Assets

**Current Assets**:
- 1000: Cash in Register
- 1010: Cash in Safe
- 1020: Bank - Operating Account (Wells Fargo #xxx1234)
- 1030: Bank - Payroll Account (Wells Fargo #xxx5678)
- 1100: Accounts Receivable (consignment sales)
- 1200: Inventory - Vinyl Records
- 1210: Inventory - Supplies & Packaging

**Fixed Assets**:
- 1500: Furniture & Fixtures
- 1510: Sound System & Equipment
- 1520: Computer & POS System
- 1590: Accumulated Depreciation

### Liabilities

**Current Liabilities**:
- 2000: Accounts Payable
- 2100: Sales Tax Payable (CA)
- 2200: Payroll Taxes Payable
- 2300: Credit Card Processing Fees Payable
- 2400: Consignment Liabilities (owed to consignors)

### Equity

- 3000: Owner's Equity
- 3100: Retained Earnings
- 3200: Current Year Profit/Loss

### Revenue

- 4000: Vinyl Sales - In Store
- 4010: Vinyl Sales - Online
- 4020: Trade-In Revenue
- 4030: Event Ticket Sales
- 4040: Workshop Fees

### Cost of Goods Sold

- 5000: Inventory Purchases - Trade-Ins (Cash)
- 5010: Inventory Purchases - Trade-Ins (Store Credit)
- 5020: Inventory Purchases - Wholesale
- 5030: Inventory Purchases - Estate/Bulk
- 5040: Inventory Purchases - Other

### Expenses

**Occupancy**:
- 6000: Rent
- 6010: Utilities
- 6020: Insurance - Property
- 6030: Property Taxes

**Payroll**:
- 6100: Wages - Full Time
- 6110: Wages - Part Time
- 6120: Payroll Taxes
- 6130: Health Insurance
- 6140: Worker's Compensation Insurance

**Operating**:
- 6200: Credit Card Processing Fees
- 6210: Bank Fees
- 6220: Office Supplies
- 6230: Packaging Materials
- 6240: Cleaning & Maintenance
- 6250: Security System

**Marketing**:
- 6300: Advertising - Online
- 6310: Social Media Marketing
- 6320: Print Materials
- 6330: Event Expenses
- 6340: Website Hosting & Maintenance

**Professional Services**:
- 6400: Accounting & Bookkeeping
- 6410: Legal Fees
- 6420: IT Support

**Other**:
- 6500: Depreciation
- 6510: Donations
- 6520: Licenses & Permits
- 6530: Miscellaneous

---

## Daily Cash Handling

### Opening Procedures

**Register Setup** (Start of Shift):
1. Count starting cash drawer: $300.00
   - 20 x $1 bills = $20.00
   - 10 x $5 bills = $50.00
   - 20 x $10 bills = $200.00
   - 6 x $5 coins (quarters) = $30.00
2. Document on cash count sheet
3. Sign and timestamp
4. Lock extra cash in safe

### During Business Hours

**Cash Drops**:
- Perform when register exceeds $500
- Count excess cash
- Complete cash drop envelope
- Place in safe drop slot
- Document in log

**Large Bills**:
- Check all $50 and $100 bills with marker
- Verify against counterfeit indicators
- Manager approval for bills over $100

### Closing Procedures

**End of Day** (Close of Business):
1. Process final transaction
2. Run Z-report (daily sales total)
3. Count all cash in register
4. Complete cash count sheet
5. Reconcile against Z-report
6. Document discrepancies (±$5 acceptable)
7. Prepare deposit
8. Lock cash in safe
9. Secure all credit card receipts

**Deposit Preparation**:
- Sort bills by denomination
- Band cash in $100 increments
- Roll coins in standard wrappers
- Complete deposit slip
- Place in bank bag
- Record total in deposit log
- Store in safe until bank run

---

## Sales Reporting

### Daily Sales Report

**Components**:
- Gross sales (before discounts)
- Discounts applied
- Net sales
- Sales tax collected
- Payment method breakdown:
  - Cash
  - Credit/Debit
  - PayPal
  - Store Credit
- Number of transactions
- Average transaction value

**Due**: By end of business day
**Submit To**: Sarah Chen (GM)

### Weekly Sales Summary

**Every Monday** (for previous week):
- Total sales by day
- Week-over-week comparison
- Best-selling items (top 10)
- Inventory additions
- Trade-in summary (cash vs. credit)
- Customer count
- Online vs. in-store breakdown

### Monthly Financial Close

**By 5th of Following Month**:
- Complete sales reconciliation
- Inventory valuation
- COGS calculation
- Accounts receivable aging (consignments)
- Accounts payable summary
- Payroll summary
- P&L statement
- Balance sheet

---

## Inventory Valuation

### Methods

**FIFO** (First-In, First-Out):
- Record acquisition cost
- Oldest inventory cost used for COGS
- Remaining inventory at current cost

**Periodic Physical Count**:
- Full inventory count: Annually (January)
- Spot checks: Monthly (random 5%)
- High-value items: Quarterly verification

### Inventory Adjustments

**Shrinkage**:
- Document missing items
- Investigate discrepancies over $100
- Write-off with manager approval
- Adjust inventory value

**Damage**:
- Document damaged items
- Markdown or disposal
- Adjust inventory value
- Track reasons (handling, shipping, etc.)

**Donations**:
- Document donated items
- Fair market value assessment
- Donation receipt issued
- Write-off against taxable income

---

## Payment Processing

### Credit Card Transactions

**Processor**: Stripe
**Merchant Account**: Misty Jazz Records LLC
**Rates**:
- In-person: 2.7% + $0.00
- Online: 2.9% + $0.30
- International: +1.5%

**Daily Reconciliation**:
- Match batch settlement to sales
- Verify all charges successful
- Document chargebacks
- Investigate discrepancies

### Refunds & Voids

**Voids** (same day):
- Void in POS system
- Cancel credit card charge
- Document reason
- Manager approval for >$100

**Refunds** (after settlement):
- Process refund in POS
- Issue credit card refund
- Document reason
- Update inventory
- Manager approval for all refunds

### Sales Tax

**California Rate**: 8.5% (San Francisco)
**Collection**: On all in-store sales
**Exemptions**: Resellers with valid permit
**Remittance**: Quarterly to CA Department of Tax and Fee Administration
**Due Dates**: April 30, July 31, October 31, January 31

**Tracking**:
- Daily sales tax collection logged
- Separate account for tax liability
- Quarterly reconciliation
- Form CDTFA-401 submitted

---

## Consignment Accounting

### Recording Consignments

**Upon Receipt**:
- Not recorded as inventory
- Liability created (amount owed to consignor)
- Tracking in separate consignment log
- Each item tagged with consignor ID

**Upon Sale**:
```
Debit: Cash/Credit Card $100.00
Credit: Consignment Sales Revenue $40.00 (our 40%)
Credit: Consignment Liability $60.00 (consignor's 60%)
```

### Monthly Payouts

**First Friday of Each Month**:
1. Generate consignment report
2. Calculate amounts owed (60% of sales)
3. Verify with consignment log
4. Prepare checks/PayPal payments
5. Email statements to consignors
6. Document all payments
7. Reduce consignment liability

**Minimum Payout**: $50 (smaller amounts carry forward)

---

## Budget & Forecasting

### Monthly Budget (2026)

**Revenue Targets**:
- January: $45,000 (post-holiday slow)
- February: $42,000
- March: $48,000
- April: $65,000 (Record Store Day)
- May-June: $50,000/month
- July-August: $45,000/month (slower)
- September-October: $52,000/month
- November: $58,000 (holiday ramp-up)
- December: $75,000 (holiday peak)
- **Annual**: $627,000

**Gross Margin Target**: 60% (COGS = 40%)

**Operating Expenses Budget**:
- Rent: $8,000/month
- Payroll: $18,000/month (includes taxes/benefits)
- Utilities: $800/month
- Insurance: $1,200/month
- Marketing: $2,000/month
- Other Operating: $3,000/month
- **Total Monthly**: ~$33,000

**Net Profit Target**: 15% of revenue

---

## Financial Controls

### Segregation of Duties

**Cash Handling**: Sales staff
**Deposits**: Manager
**Bookkeeping**: Pat Anderson
**Bank Reconciliation**: Sarah Chen
**Financial Review**: Duke Wellington

**No Single Person** controls entire transaction cycle

### Authorization Limits

**Purchases**:
- <$500: Any manager
- $500-$2,000: General Manager
- >$2,000: Owner approval

**Refunds**:
- <$50: Sales staff
- $50-$200: Manager
- >$200: General Manager or Owner

**Write-Offs**:
- Inventory <$100: Manager
- Inventory >$100: Owner
- Bad debt: Owner only

---

## Tax Compliance

### Business Taxes

**Federal**:
- Form 1120S (S-Corporation): Due March 15
- Estimated quarterly payments
- W-2s for employees: Due January 31
- 1099s for contractors: Due January 31

**State of California**:
- CA Form 100S: Due March 15
- Sales tax: Quarterly
- Employer payroll taxes: Monthly
- Workers' comp insurance: Annual premium

**Local**:
- Business license: Annual renewal (January)
- SF Business Registration Fee

### Record Retention

**Permanent**:
- Corporate documents
- Financial statements
- Audit reports

**7 Years**:
- Tax returns & supporting docs
- Payroll records
- Sales records
- Expense receipts

**3 Years**:
- Bank statements
- Cancelled checks
- Credit card statements

---

## Banking Relationships

### Primary Bank: Wells Fargo

**Contacts**:
- Business Banker: Jennifer Wong (415-555-9100)
- Branch: Castro Street
- Online Banking: business.wellsfargo.com

**Services**:
- Business checking
- Business savings
- Merchant services
- Payroll service
- Business credit card

**Schedule**:
- Deposits: Daily
- Reconciliation: Weekly
- Statement review: Monthly

---

## Key Performance Indicators

### Monitor Monthly

**Revenue Metrics**:
- Total sales
- Average transaction value
- Transactions per day
- Online vs. in-store mix
- Year-over-year growth

**Profitability**:
- Gross margin %
- Net profit %
- Revenue per square foot
- Revenue per employee hour

**Inventory**:
- Inventory turnover rate (goal: 3-4x/year)
- Days in inventory (goal: 90-120 days)
- Inventory-to-sales ratio
- Shrinkage rate (goal: <1%)

**Cash Flow**:
- Cash on hand
- Days cash on hand (goal: 60+ days)
- Accounts receivable aging
- Debt service coverage

---

## Financial Software

**Accounting**: QuickBooks Online Plus
**POS System**: Square for Retail
**Payroll**: Gusto
**Time Tracking**: When I Work
**Expense Tracking**: Expensify

**Integration**: All systems sync to QuickBooks

---

## Emergency Procedures

### Cash Shortage

1. Recount carefully
2. Check for misplaced transactions
3. Review tape (if available)
4. Document discrepancy
5. Manager investigates
6. If >$50: Formal investigation
7. Pattern of shortages: Disciplinary action

### Cash Over

1. Recount carefully
2. Check for wrong change given
3. Document overage
4. Held for 30 days for customer claim
5. After 30 days: Revenue

### System Failure

**Backup Procedures**:
- Manual credit card imprints (if available)
- Hand-written receipts
- Log all transactions
- Process when system restored
- Reconcile carefully

---

## Contact Information

**Bookkeeper**: Pat Anderson
- Email: pat@mistyjazzrecords.com
- Phone: (415) 555-5208
- Available: Tuesday/Thursday 9 AM - 3 PM

**General Manager**: Sarah Chen
- Email: sarah@mistyjazzrecords.com
- Phone: (415) 555-5202

**Owner**: Duke Wellington
- Email: duke@mistyjazzrecords.com
- Phone: (415) 555-5201

**CPA Firm**: Anderson & Associates
- Contact: Michael Anderson, CPA
- Phone: (415) 555-7700
- Email: manderson@andersoncpa.com

---

*This guide contains confidential financial information. Do not share outside management.*

*Last Updated: January 2026*