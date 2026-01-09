# Misty Jazz Records - Online Store Operations

## E-Commerce Platform Overview

**Website**: www.mistyjazzrecords.com
**Platform**: Shopify Plus
**Payment Processor**: Stripe
**Shipping Integration**: ShipStation

---

## Product Listings

### Photography Standards

**Equipment**:
- Canon EOS R6 (main camera)
- 50mm f/1.8 lens
- Ring light
- White backdrop
- Copy stand

**Photo Requirements**:
- **Front Cover**: Full, straight-on, well-lit
- **Back Cover**: Full, readable track listing
- **Vinyl**: Out of sleeve, showing label
- **Special Features**: Inserts, booklets, posters
- **Damage**: Close-ups of any condition issues

**Specifications**:
- Resolution: 2000px minimum width
- Format: JPEG
- File size: Under 2MB
- Background: Pure white (#FFFFFF)
- No watermarks

### Product Information

**Required Fields**:
- Title (Artist - Album Title)
- Artist name
- Album title
- Label
- Catalog number
- Format (LP, 12", 10", 7")
- Speed (33⅓, 45, 78 RPM)
- Pressing details (year, country, variant)
- Condition (Media / Sleeve)
- Price

**Description Template**:
```
[Album Title] by [Artist]

Original [Year] pressing on [Label].

CONDITION:
Vinyl: [Grade] - [Specific details]
Cover: [Grade] - [Specific details]

[Additional notes about pressing, sound quality, collectibility]

All records are carefully inspected, cleaned if needed, and packaged to prevent shipping damage.

30-day return policy. Questions? Contact us anytime!
```

**Grading**:
- Use standard Goldmine grading (M, NM, VG+, VG, G+, G, P)
- Be conservative (slightly undergrade)
- Mention specific flaws
- Note any play testing results

**SEO Optimization**:
- Keywords in title
- Detailed description
- Alt text for images
- Tags: Genre, artist, label, era

### Pricing Online

**Formula**: In-store price + $2-5 (reflects photography/listing labor)

**Compare**:
- Discogs current listings
- eBay sold listings
- Other online retailers

**Dynamic Pricing**:
- Adjust based on demand
- Seasonal promotions
- Clearance (slow movers)

---

## Order Processing

### Order Receipt

**Automated Notifications**:
- Customer: Order confirmation email (immediate)
- Store: Email + SMS to fulfillment staff
- Dashboard: Order appears in ShipStation

**Order Review** (Within 2 hours):
1. Verify payment processed
2. Check shipping address (valid format)
3. Confirm item still in stock
4. Flag any issues (fraud check, address problems)

### Fraud Prevention

**Red Flags**:
- Shipping to freight forwarder
- Billing and shipping address mismatch
- Large order, new customer
- International high-risk country
- Multiple orders, different cards, same address

**Verification Steps**:
1. Check AVS (Address Verification System)
2. Verify CVV code
3. Review customer history
4. Call customer if suspicious
5. Cancel and refund if unable to verify

**Stripe Radar**: Automatically flags high-risk transactions

---

## Fulfillment Process

### Daily Order Workflow

**Morning (10:00 AM)**:
1. Pull overnight orders
2. Print packing slips
3. Gather items from inventory
4. Double-check item against order
5. Verify condition matches listing

**Packing Procedure**:
1. Clean record if needed
2. Place vinyl in protective inner sleeve
3. Remove vinyl from cover (prevent seam splits)
4. Place cover in plastic outer sleeve
5. Insert both in LP mailer with cardboard stiffeners
6. Add "Fragile" and "Do Not Bend" stickers
7. Seal securely

**High-Value Items** ($100+):
- Double-box method
- Extra padding
- Signature required
- Full insurance

**Label Creation**:
1. Enter package details in ShipStation
2. Select appropriate service level
3. Print label
4. Affix to package
5. Update order status to "Shipped"

**Shipping Cutoff**: 2:00 PM for same-day pickup

### Quality Control

**Before Shipping**:
- [ ] Correct item
- [ ] Condition as described
- [ ] All components present
- [ ] Vinyl removed from cover
- [ ] Protective sleeves
- [ ] Proper padding
- [ ] Label correct address
- [ ] Tracking number in system

**Random Audits**: Manager checks 10% of outgoing packages

---

## Shipping Management

### Shipping Rates (Calculated at Checkout)

**Domestic** (USPS Media Mail):
- 1 LP: $5.00 flat
- 2-3 LPs: $7.00 flat
- 4+ LPs: $2.00 per additional

**Domestic** (USPS Priority):
- Available at checkout
- Calculated by weight and zone

**International**:
- USPS First Class International
- USPS Priority Mail International
- Calculated by weight and destination

**Free Shipping**:
- Domestic orders $100+
- Automatically applied at checkout

### Tracking & Customer Communication

**Automated Emails**:
1. **Order Confirmed**: Immediate
2. **Order Shipped**: Within 2 hours of fulfillment
   - Includes tracking number
   - Estimated delivery date
   - Link to carrier tracking
3. **Delivered**: 24 hours after delivery confirmation

**Proactive Communication**:
- Delays: Email customer immediately
- Stock issues: Contact within 4 hours
- Shipping problems: Track and reach out before customer

---

## Returns & Exchanges (Online)

### Return Process

**Customer Initiates**:
1. Customer emails support@mistyjazzrecords.com
2. Provide order number and reason
3. Photos required for damage claims

**Staff Response** (Within 24 hours):
1. Review order and reason
2. Approve return (send RMA number)
3. Provide return shipping label (if our error)
4. Set expected refund timeline

**Return Received**:
1. Inspect item condition
2. Verify matches original description
3. Process refund (5-7 business days to original payment)
4. Return to inventory or adjust
5. Email customer confirmation

**Our Error / Defective**:
- Prepaid return label provided
- Refund shipping costs both ways
- Express replacement offered
- 10% discount code for future purchase

**Customer Change of Mind**:
- Customer pays return shipping
- Restocking fee: None (if returned in same condition)
- Must be within 30 days

---

## Customer Service (Online)

### Response Time Standards

**Email**: support@mistyjazzrecords.com
- **Business Hours**: Within 4 hours
- **After Hours**: Next business day
- **Weekends**: Monday response

**Live Chat**: Available during business hours
- Instant response goal
- Staff rotates monitoring

**Social Media**: @mistyjazzrecords
- Instagram DMs: Within 2 hours
- Facebook Messages: Within 4 hours
- Comments: Daily monitoring

### Common Inquiries

**"When will my order ship?"**
- Orders placed before 2 PM ship same day
- Processing time: 1-2 business days
- Tracking provided via email

**"Can I change my order?"**
- Before shipping: Yes, contact immediately
- After shipping: No, use return process

**"What condition is this record?"**
- Check listing photos and description
- Contact for additional photos/info
- Play-test available on request

**"Do you ship to [country]?"**
- Yes, we ship worldwide
- Rates calculated at checkout
- Customs fees customer responsibility

**"Is this the original pressing?"**
- Check listing for pressing details
- Verify with Discogs if needed
- Contact for pressing verification

---

## Inventory Sync

### Stock Management

**Real-Time Inventory**:
- In-store POS system syncs with Shopify
- Record sold online: Removed from in-store inventory
- Record sold in-store: Removed from website

**Stock Levels**:
- All items: Quantity = 1 (one-of-a-kind)
- Automatic removal when sold
- Manual check weekly for accuracy

**Preventing Oversell**:
- Daily inventory reconciliation
- Flag discrepancies immediately
- Never list item not in physical possession

---

## Website Maintenance

### Daily Tasks

**Morning Checklist**:
- [ ] Check overnight orders
- [ ] Review customer inquiries
- [ ] Monitor website performance
- [ ] Check for out-of-stock items (shouldn't be any)
- [ ] Review analytics

**Weekly Tasks**:
- Upload new listings (20-30 records)
- Remove sold items (auto, but verify)
- Update homepage featured items
- Review and respond to reviews
- Check for broken links/images

**Monthly Tasks**:
- Analyze sales data
- Update SEO keywords
- Review pricing strategy
- Update blog content
- Newsletter campaign

### Content Updates

**Homepage**:
- Hero banner: Rotates featured items
- New arrivals: Auto-updates
- Staff picks: Updated bi-weekly
- Upcoming events: Updated weekly

**Blog** (SEO & Engagement):
- New post: Bi-weekly minimum
- Topics: New arrivals, artist spotlights, jazz history, collecting tips
- Goal: 800-1,200 words
- Include internal links to products

---

## Marketing & Promotions

### Email Marketing

**Newsletter** (Mailchimp):
- Frequency: Weekly (Thursdays, 10 AM)
- Subscribers: ~3,500
- Open rate target: 25%+
- Click rate target: 5%+

**Content**:
- New arrivals (top 10)
- Staff picks
- Upcoming events
- Exclusive online deals
- Jazz education/history

### Social Media

**Instagram** (@mistyjazzrecords):
- Posts: 5-7 per week
- Stories: Daily
- Reels: 2-3 per month
- Content: New arrivals, vintage finds, behind-the-scenes, staff picks

**Facebook**:
- Posts: 3-4 per week
- Events: All store events
- Engagement: Respond to comments/messages
- Community building

**Twitter/X**:
- Real-time updates
- New arrival announcements
- Engage with jazz community
- Share jazz news/history

### Promotions

**Recurring**:
- First-time customer: 10% off (auto-applied)
- Newsletter signup: $5 off next purchase
- Referral program: $10 credit (referrer & referee)

**Seasonal**:
- Record Store Day: Exclusive online releases
- Holiday season: Gift guides, free shipping
- Birthday: 15% off (email subscribers)
- Anniversary sale (May): Storewide 20% off

---

## Analytics & Reporting

### Key Metrics (Monitor Weekly)

**Sales**:
- Total online revenue
- Number of orders
- Average order value
- Online vs. in-store mix

**Traffic**:
- Unique visitors
- Page views
- Bounce rate
- Top pages

**Conversion**:
- Conversion rate (goal: 2-3%)
- Cart abandonment rate
- Email opt-in rate

**Customer**:
- New vs. returning
- Customer lifetime value
- Geographic distribution

### Tools

**Google Analytics**: Traffic and behavior
**Shopify Analytics**: Sales and products
**Mailchimp**: Email performance
**Stripe Dashboard**: Payment processing
**ShipStation**: Shipping metrics

---

## Technical Support

### Common Issues

**Website Down**:
1. Check Shopify status page
2. Clear cache and retry
3. Contact Shopify support if needed
4. Post social media update
5. Enable maintenance mode if extended

**Payment Processing Issues**:
1. Check Stripe dashboard
2. Verify card processing functioning
3. Test transaction
4. Contact Stripe support
5. Accept alternative payment (phone order)

**Inventory Sync Problems**:
1. Check POS-Shopify connection
2. Manual inventory count
3. Reconcile discrepancies
4. Contact tech support (Michael Torres)

---

## Platform Access

**Shopify Admin**:
- Owner: Full access
- General Manager: Full access
- Online Manager: Product/order access
- Staff: Order view only

**ShipStation**:
- Fulfillment staff: Full access
- Management: Full access

**Email/Social**:
- Marketing team: Full access
- Staff: View only

---

## Security

**Account Security**:
- Strong passwords (minimum 12 characters)
- Two-factor authentication required
- Password changes: Quarterly
- Activity logs: Monitored

**Customer Data**:
- PCI compliant (Stripe)
- SSL certificate (HTTPS)
- Data encryption
- Privacy policy compliance
- GDPR compliant (international)

**Backup**:
- Daily automatic backups
- Monthly manual backup download
- Stored securely offsite

---

## Contact Information

**Online Manager**: Michael Torres
- Email: michael@mistyjazzrecords.com
- Phone: (415) 555-5209

**Fulfillment**: Diana Foster
- Email: diana@mistyjazzrecords.com
- Phone: (415) 555-5207

**Customer Service**: support@mistyjazzrecords.com
**Technical Issues**: tech@mistyjazzrecords.com

---

*Procedures reviewed quarterly*
*Last Updated: January 2026*