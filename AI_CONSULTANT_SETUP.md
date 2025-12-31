# 🤖 AI Business Consultant Setup Guide

## Overview

The AI Business Consultant is an intelligent agent that analyzes your Supabase database and generates comprehensive business consultation reports using:

- **Gemini 2.0 Flash Exp** - Latest AI model for analysis
- **Langsmith** - Full tracing and observability
- **Real-time Supabase data** - Your actual business metrics

## Features

### 1. **Full Business Consultation Reports**
Generate comprehensive reports covering:
- Executive Summary
- Revenue Analysis
- Customer Strategy
- Inventory Optimization
- Product Strategy
- Risk Assessment
- Prioritized Action Plan with ROI projections

### 2. **Focused Analysis**
Choose specific areas to deep-dive:
- **Overall Business Health** - Complete business analysis
- **Revenue Optimization** - Pricing, upselling, growth strategies
- **Customer Strategy** - Retention, acquisition, VIP management
- **Inventory Management** - Stock optimization, reordering

### 3. **Quick Insights**
Get 5 actionable insights instantly with:
- Priority level (High/Medium/Low)
- Specific action to take
- Expected business impact

### 4. **Langsmith Tracing**
Every AI consultation is traced with Langsmith for:
- Full observability of AI reasoning
- Performance monitoring
- Debugging and optimization
- Cost tracking

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `langsmith>=0.1.0` - For tracing
- `google-genai>=0.3.0` - For Gemini API
- All other required packages

### Step 2: Configure Environment Variables

Add to your `.env` file:

```env
# Gemini API (required)
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase (required)
SUPABASE_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_secret_key

# Langsmith (required for tracing)
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=misty-ai-enterprise
```

### Step 3: Get Langsmith API Key

1. Go to [Langsmith](https://smith.langchain.com/)
2. Sign up or log in
3. Create a new project called `misty-ai-enterprise`
4. Go to Settings → API Keys
5. Create a new API key
6. Add it to your `.env` file

### Step 4: Run the Application

```bash
streamlit run main.py
```

Navigate to **Analytics** → **AI Predictions** tab

## How to Use

### Generate a Full Report

1. Select **Consultation Focus**:
   - Overall Business Health (recommended for first-time)
   - Revenue Optimization
   - Customer Strategy
   - Inventory Management

2. Select **Report Style**:
   - Executive Summary (quick overview)
   - Detailed Analysis (comprehensive)
   - Quick Insights (5 bullet points)

3. Click **🎯 Generate Report**

4. Wait 10-30 seconds for AI analysis

5. Review the generated consultation

6. Download the report using **📥 Download Report**

### View Langsmith Traces

1. Go to https://smith.langchain.com/
2. Select your project (`misty-ai-enterprise`)
3. View all AI consultation traces
4. See:
   - Input data (metrics gathered)
   - Prompt used
   - AI response
   - Latency and token usage
   - Costs

## What the AI Analyzes

The AI consultant automatically gathers and analyzes:

### Financial Metrics
- Total revenue
- Total orders
- Average order value

### Customer Metrics
- Total customers
- Top 5 customers by spending
- Average customer rating
- Total reviews

### Inventory Metrics
- Total albums in catalog
- Inventory value
- Stock level distribution
- Low stock alerts

### Product Performance
- Top 10 selling albums
- Top 5 rated albums
- Genre performance
- Record label performance

### Payment Analytics
- Payment method distribution
- Payment success/failure rates

## Example Reports

### Overall Business Health Report

The AI will provide:

1. **Executive Summary**
   - Overall business health score
   - Key highlights
   - Major concerns

2. **Revenue Analysis**
   - Revenue trends
   - Opportunities to increase AOV
   - Pricing recommendations

3. **Customer Strategy**
   - VIP customer programs
   - Retention strategies
   - Acquisition tactics

4. **Inventory Optimization**
   - Reordering priorities
   - Overstock management
   - Supplier relationships

5. **Product Strategy**
   - Which albums/genres to promote
   - Bundling opportunities
   - New product suggestions

6. **Risk Assessment**
   - Payment failures
   - Stock-outs
   - Customer churn

7. **Action Plan**
   - Top 5 prioritized actions
   - Expected ROI for each
   - Implementation timeline

### Quick Insights Example

```
🔴 Insight #1: Low stock alert on bestsellers
Priority: High
Action: Immediately reorder "All Blues" and 3 other top sellers
Expected Impact: Prevent $12,000 in lost sales

🟡 Insight #2: VIP customer engagement opportunity
Priority: Medium
Action: Create loyalty program for top 10 customers
Expected Impact: Increase repeat purchase rate by 25%
```

## Customization

### Add Custom Analysis

Edit `frontend/utils/ai_business_consultant.py`:

```python
@traceable(name="your_custom_analysis")
def analyze_custom_metric(self) -> Dict[str, Any]:
    # Your custom analysis logic
    metrics = self.analytics.get_your_custom_data()

    # Build prompt
    prompt = f"Analyze this custom metric: {metrics}"

    # Generate with Gemini
    response = self.gemini_client.models.generate_content(...)

    return response
```

### Change AI Model

In `ai_business_consultant.py`, update the model:

```python
response = self.gemini_client.models.generate_content(
    model='gemini-2.0-flash-exp',  # Change this
    contents=prompt,
    config=self.generation_config
)
```

Available models:
- `gemini-2.0-flash-exp` (fastest, recommended)
- `gemini-1.5-pro` (most capable)
- `gemini-1.5-flash` (balanced)

### Adjust AI Personality

Modify the system instruction in `__init__`:

```python
self.generation_config = types.GenerateContentConfig(
    system_instruction=[
        "Your custom instructions here",
        "Change tone, focus, style, etc."
    ],
    temperature=0.7,  # 0=deterministic, 1=creative
    top_p=0.95,
    top_k=40,
)
```

## Troubleshooting

### Error: "Failed to initialize AI consultant"

**Solution:** Check your `.env` file has:
- `GEMINI_API_KEY`
- `LANGSMITH_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`

### Langsmith traces not appearing

**Solution:** Make sure you have:
```env
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=misty-ai-enterprise
```

### Report generation is slow

**Solution:**
- Normal: 10-30 seconds for full reports
- Use "Quick Insights" for faster results (3-5 seconds)
- Check Langsmith for latency breakdown

### AI responses are generic

**Solution:**
- Make sure you have real data in Supabase
- Try different consultation focuses
- Adjust temperature in `generation_config`

## Best Practices

1. **Generate reports weekly** to track trends
2. **Download and compare** reports over time
3. **Use Langsmith** to optimize prompts
4. **Start with Quick Insights** for rapid analysis
5. **Follow up with focused reports** on problem areas

## Cost Monitoring

### Gemini API Costs
- Track in Google Cloud Console
- Gemini 2.0 Flash is very cost-effective
- Typical report: ~$0.01-0.05

### Langsmith Costs
- Free tier: 5,000 traces/month
- More than enough for weekly reports
- Upgrade if needed

## Next Steps

1. Generate your first report
2. Review in Langsmith
3. Implement top recommendations
4. Schedule weekly analysis
5. Track improvements in metrics

---

**Questions?** Check the Langsmith traces to see exactly what data is being analyzed and how the AI is reasoning.
