# UseAutumn Integration Setup for PayTosha

## Overview
PayTosha now integrates with UseAutumn for dynamic, context-aware pricing and billing management. UseAutumn handles all the complexity of subscriptions, upgrades, downgrades, usage tracking, and feature gating.

## What UseAutumn Provides
- **attach**: Generates Stripe Checkout URLs for purchases/upgrades
- **check**: Verifies if users can access features
- **track**: Records usage events for billing
- **identify**: Registers users in the billing system

## Setup Steps

### 1. Get UseAutumn API Key
1. Sign up at [useautumn.com](https://useautumn.com)
2. Create a new project
3. Get your API key from the dashboard

### 2. Configure Environment Variables
Add to your `.env` file:
```env
USEAUTUMN_API_KEY=your_useautumn_api_key_here
USEAUTUMN_BASE_URL=https://api.useautumn.com/v1
```

### 3. Configure Products in UseAutumn Dashboard
Create these products in your UseAutumn dashboard:

#### Free Plan
- Product ID: `free_plan`
- Price: $0
- Features: `basic_marketplace`, `limited_crawls`, `basic_analytics`
- Limits: 10 crawls/month, 5 products listed, 100 analytics views

#### Fair Plan
- Product ID: `fair_plan`
- Price: $9.99
- Features: `marketplace`, `social_crawls`, `advanced_analytics`, `fair_pricing`
- Limits: 100 crawls/month, 50 products listed, 1000 analytics views

#### Premium Plan
- Product ID: `premium_plan`
- Price: $29.99
- Features: `unlimited_marketplace`, `unlimited_crawls`, `premium_analytics`, `priority_support`
- Limits: Unlimited

### 4. Configure Stripe Integration
1. Connect your Stripe account in UseAutumn dashboard
2. Set up webhook endpoints for subscription events
3. Configure success/cancel URLs

## How It Works

### User Registration
When a user registers:
1. PayTosha analyzes their context (location, device, persona)
2. User is identified in UseAutumn system
3. Recommended plan is calculated based on context
4. User gets assigned to appropriate tier

### Dynamic Pricing
- Students automatically get free plan
- Users in developing countries get fair pricing
- High-income users get premium recommendations
- Device and browser context influence pricing

### Feature Access
Before accessing features, PayTosha checks:
```python
# Check if user can access feature
entitlement = await useautumn_service.check_entitlement(user_id, "unlimited_crawls")
if entitlement["allowed"]:
    # Allow access
    await useautumn_service.track_usage(user_id, "crawls", 1)
```

### Upgrades
Users can upgrade via:
1. Pricing page shows recommended plan
2. Click upgrade button
3. UseAutumn generates Stripe checkout URL
4. User completes payment
5. Subscription is automatically activated

## API Endpoints

### UseAutumn Routes
- `POST /useautumn/identify/{user_id}` - Identify user in system
- `POST /useautumn/attach/{user_id}/{product_id}` - Generate checkout URL
- `POST /useautumn/check/{user_id}/{feature_id}` - Check feature access
- `POST /useautumn/track/{user_id}/{feature_id}` - Track usage
- `GET /useautumn/subscription/{user_id}` - Get subscription details
- `GET /useautumn/recommend-plan/{user_id}` - Get recommended plan
- `GET /useautumn/plans` - Get all available plans
- `POST /useautumn/webhook` - Handle webhooks

### Helper Routes
- `GET /pricing` - Dynamic pricing page
- `GET /api/user-context/{username}` - Get user context
- `GET /api/user/{username}` - Get user data

## Testing

### 1. Start the Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test User Registration
1. Go to `/register`
2. Create a new user
3. Check logs for UseAutumn integration

### 3. Test Pricing Page
1. Go to `/pricing?username=your_username`
2. View context profile and recommended plan
3. Test upgrade flow

### 4. Test Feature Access
```bash
# Check if user can access feature
curl -X POST "http://localhost:8000/useautumn/check/user_id/feature_id"

# Track usage
curl -X POST "http://localhost:8000/useautumn/track/user_id/feature_id" \
  -H "Content-Type: application/json" \
  -d '{"value": 1}'
```

## Troubleshooting

### Common Issues
1. **API Key Error**: Check your UseAutumn API key in `.env`
2. **Product Not Found**: Ensure products are created in UseAutumn dashboard
3. **Webhook Errors**: Check webhook configuration in UseAutumn
4. **Stripe Integration**: Verify Stripe connection in UseAutumn

### Debug Logs
Check server logs for:
- User identification status
- Recommended plan calculations
- Feature access checks
- Usage tracking events

## Next Steps
1. Set up production UseAutumn instance
2. Configure Stripe webhooks
3. Test complete billing flow
4. Monitor usage and billing metrics
5. Implement advanced feature gating

## Support
- UseAutumn Documentation: [docs.useautumn.com](https://docs.useautumn.com)
- PayTosha Issues: Create GitHub issue
- UseAutumn Support: Contact via their website 