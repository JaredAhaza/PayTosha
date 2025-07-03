# PayTosha
PayTosha is a personalized pricing platform that adapts subscription fees, language, and UI based on user context. Built with FastAPI, Supabase, UseAutumn, Lingo.dev, and Tambo — because software should adapt to the user, not the other way around.

## 🔧 Tech Stack
| Layer             | Technology                                                |
| ----------------- | --------------------------------------------------------- |
| Backend           | Python, FastAPI                                           |
| Frontend          | TailwindCSS, Alpine.js *(or React)*                       |
| Database          | Supabase (PostgreSQL)                                     |
| Authentication    | BetterAuth                                                |
| Contextual Tools  | Tambo (UI), Lingo.dev (localization), UseAutumn (pricing) |
| Notifications     | Resend                                                    |
| Deployment        | Vercel / Railway / Render                                 |
| Optional AI Layer | Python + LLM API                                          |

## 🔁 System Flow
1. User Visits Site:
System captures basic context: location, device, and language preference.

2. Onboarding & Auth:
User signs up using BetterAuth, and we collect additional context (e.g., region, student status, income level if shared).

3. Context Processing:
Backend classifies user into a pricing tier using UseAutumn and stores context in Supabase.

4. Personalization:

UI adapts with Tambo (e.g., mobile-optimized for low-end devices)

Language localized via Lingo.dev

Pricing adjusted for fairness via UseAutumn

5. Notifications:
Emails sent via Resend (confirmation, usage summaries, reminders)

6. Admin Panel:
Admin sees user breakdown and can override pricing manually if needed.

## 🚀 Development Flow (Kanban Board)

### Board Title: PayTosha – Dev Roadmap
Columns:

✅ To Do

🔨 In Progress

🧪 Testing

🚀 Deployed

Each card/task will represent a milestone or feature.

Here’s the list of cards to pre-fill in your board:

🔹 Ideation & Planning
Finalize concept, brand name, tagline

Define user personas and pricing tiers

Create system architecture flow

🔹 UI & Design
Draft landing page wireframe

Sketch onboarding flow

Design dashboard layout (with adaptive UI in mind)

Prepare localized content (for Lingo.dev)

🔹 Backend Development
Set up FastAPI project

Create models: User, ContextProfile, PricingTier

Integrate Supabase

Add tier logic for UseAutumn

Add localization endpoints

🔹 Frontend Integration
Build signup page + dashboard

Add TailwindCSS + mobile-first layout

Fetch personalized pricing

Adapt layout with Tambo

🔹 Notifications
Set up Resend for welcome emails

Create personalized plan summary email

🔹 Deployment
Deploy backend to Railway or Render

Deploy frontend to Vercel

Configure domain + SSL

🔹 Demo & Pitch
Record a 60-second walkthrough

Write Devpost + submission copy

Tweet and Discord submission
