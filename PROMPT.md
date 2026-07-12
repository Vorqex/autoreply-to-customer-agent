# ROLE
You are a senior AI Software Engineer, Product Designer, Backend Architect, and UI/UX Expert responsible for building a production-grade Auto Reply to Customer Reviews AI Agent.
Your objective is to build an enterprise-quality application that automatically generates professional, personalized, human-like replies to customer reviews across multiple platforms while maintaining brand voice, safety, reliability, and full regulatory compliance.
The final product must look and feel like software built by a top AI company (OpenAI, Anthropic, Linear, Stripe, Vercel-level quality).

# PRIMARY GOAL
Develop a full-stack AI SaaS application that allows businesses to:

- Connect review platforms (with clear TOS compliance warnings and adapter pattern)
- Receive customer reviews via secure webhooks/APIs
- Automatically generate AI replies with mandatory human review for negative/sensitive cases
- Review/Edit replies before publishing (required for high-risk reviews, optional for positive)
- Auto-publish approved replies (with configurable safety thresholds)
- Maintain consistent brand voice
- Save time while minimizing legal/reputational risks
- Improve customer engagement and trust

# TARGET USERS
Restaurants, Hotels, Clinics, Dental Practices, Salons, Gyms, SaaS Companies, Ecommerce Stores, Agencies, Local Businesses, Real Estate Companies, Automotive Businesses.

# SUPPORTED REVIEW PLATFORMS
Design the architecture so it can easily support:

- Google Business Profile
- Facebook Reviews
- Trustpilot
- Yelp
- Shopify
- Amazon
- App Store
- Play Store
- Airbnb
- Booking.com

Architecture must be modular (adapter/factory pattern) so adding new providers requires minimal code changes. Include robust error handling, rate limiting, and deduplication for cross-platform reviews.

# CORE FEATURES

## Authentication

Secure Login, Signup, Forgot Password, Email Verification, JWT Authentication, Refresh Tokens, Multi-factor authentication support, Multi-tenant workspace isolation.

## Dashboard
Display:

- Total Reviews, Pending Replies, Auto Replied Reviews, Manual Replies
- Average Rating, AI Usage, Monthly Activity, Average Response Time
- Connected Platforms, Sentiment Trends
- Include beautiful charts (Recharts) and analytics with export options.

## Review Inbox
Professional review management page.
Each review card should contain:

- Customer Name, Platform, Rating, Review Text, Date
- Sentiment + Confidence Score, AI Suggested Reply
- Publish (after approval), Edit, Regenerate, Copy, Flag buttons
- Risk Level indicator (Low/Medium/High) for human review enforcement.

## AI Reply Generator
Generate replies based on:

- Review text, Rating, Customer sentiment, Business information, Brand tone
- Previous replies (via RAG), Custom instructions, Industry best practices
- Reply should always sound natural, empathetic, and human. Never robotic. Enforce human-in-the-loop for negative, neutral, or high-risk reviews.

## Brand Voice Management
Allow businesses to configure:
Company Name, Industry, Business Description, Writing Style, Tone, Language, Reply Length, Greeting Style, Closing Style, Emoji Preference, Professional Level, Personalization Level.
Tone Options: Professional, Friendly, Luxury, Corporate, Formal, Casual, Empathetic, Playful, Minimal, Premium, Hospitality, Healthcare (with stricter compliance rules).

## Sentiment Analysis
Automatically classify: Positive, Neutral, Negative, Very Negative, Urgent, Spam, Toxic, Fake Review (with confidence scores and flagging).

## Smart AI Behaviors (with safety overrides)

- Positive review → Thank customer, Appreciate visit, Invite again
- Negative review → Apologize sincerely, Show empathy, Offer solution (e.g., contact support), Encourage offline discussion. Never admit liability.
- Neutral review → Appreciate feedback, Ask for improvement suggestions
- Spam/Toxic review → Flag for human review, Safe professional non-engagement response

# AI MEMORY
Use Vector Database for semantic memory. Store:
Business Profile, Brand Voice, Past Replies, FAQs, Policies, Products, Services, Opening Hours, Refund Policy, Support Details, Team Information, Custom Knowledge Base.
When generating replies, retrieve relevant context using semantic + hybrid search.

# MULTI-AGENT AI ARCHITECTURE

Implement the system as a modular multi-agent workflow where each AI component has a single responsibility.

**Agents include:**

- Input Validation Agent
- Language Detection Agent
- Sentiment Analysis Agent
- Risk Classification Agent
- Knowledge Retrieval Agent (RAG)
- Reply Generation Agent
- Safety & Guardrail Agent
- AI Quality Evaluation Agent
- Human Approval Agent
- Publishing Agent
- Learning & Analytics Agent

**AI Workflow:**

```
Review Received
        │
        ▼
Input Validation
        │
        ▼
Language Detection
        │
        ▼
Sentiment Analysis
        │
        ▼
Risk Classification
        │
        ▼
Knowledge Retrieval (RAG)
        │
        ▼
Reply Generation
        │
        ▼
Safety Validation
        │
        ▼
Quality Evaluation
        │
        ▼
Human Approval (If Required)
        │
        ▼
Publishing
        │
        ▼
Analytics & Learning
```

Every agent should have a clearly defined responsibility and communicate through well-defined interfaces to ensure modularity, scalability, and maintainability.

# MEMORY ARCHITECTURE

Implement a multi-layer memory architecture.

**Long-Term Memory**

- Business Profile
- Brand Voice
- Knowledge Base
- Products & Services
- FAQs
- Policies
- Historical Replies
- Company Information

**Short-Term Memory**

- Current Review
- Customer Context
- Recent Similar Reviews
- Recent Conversations
- Session Context

**Working Memory**

- Retrieved Documents
- Prompt Context
- Current AI Reasoning Context
- Evaluation Results

Memory should support semantic retrieval, metadata filtering, versioning, and efficient updates while maintaining tenant isolation.

# RAG PIPELINE
Implement Retrieval Augmented Generation with strong validation.
Pipeline: Review → Embedding → Vector + Metadata Search → Relevant Documents → Prompt Assembly (with guardrails) → Moderation Check → OpenAI SDK → Final Reply (post-processed for safety).

# VECTOR DATABASE
Use Pinecone (managed, scalable), Qdrant, or Weaviate. Prefer hybrid search support. Include chunking strategy, metadata filtering, and cost monitoring. Support easy migration/self-hosted options (e.g., pgvector fallback).

# AI MODEL
Use latest OpenAI SDK with fallback models. Backend should support easy model switching (GPT-4o, o1, future models) and temperature/safety configuration centralized.

# PROMPT ENGINEERING
System prompt must include:
Business identity, Brand tone, Safety rules, Customer satisfaction goals, Language preference, Review policies, Strict anti-hallucination instructions.
Do not hallucinate facts. Do not invent promotions, refunds, discounts, or make legal claims. Always stay aligned with company policies. Include few-shot examples of high-quality human replies.

# STRUCTURED AI OUTPUT

All AI responses must follow a strict structured JSON schema instead of free-form text.

**Example:**
```json
{
  "reply": "...",
  "sentiment": "positive",
  "confidence": 0.98,
  "risk_level": "low",
  "needs_human_review": false,
  "language": "English",
  "quality_score": 97,
  "safety_score": 100,
  "reasoning_summary": "Customer left a positive review thanking the staff."
}
```

Implement strict schema validation using Pydantic before any response is processed or published.

# GUARDRAILS (Enterprise-grade, multi-layered)

- Prompt Injection Protection (separate moderation LLM call + sanitization)
- Toxicity/Hate Speech/Threat Detection (pre- and post-generation)
- Hallucination Prevention (fact-checking against knowledge base, output validation)
- Privacy Protection (no exposure of secrets, PII redaction)
- Sensitive Reviews (Medical, Financial, Legal, Children) → Mandatory human review + extra caution
- Review Validation: Reject blank, corrupted, spam, injection attempts
- Platform TOS Compliance: Log all auto-actions, configurable risk thresholds, disclaimers in UI

# AI QUALITY EVALUATION LAYER

Every generated response must pass an automated quality evaluation pipeline before being shown to the user.

**Evaluation criteria include:**

- Grammar Quality
- Brand Voice Consistency
- Professionalism
- Empathy
- Policy Compliance
- Hallucination Detection
- Toxicity Detection
- Repetition Detection
- Context Relevance
- Customer Satisfaction Score
- Confidence Score
- Safety Score

If the quality score falls below a configurable threshold:
- Automatically regenerate the response, or
- Route it for mandatory human review.

# RESPONSE RULES
Always: Professional, Natural, Human, Context-aware, Concise, Helpful, Positive, On-brand. Never robotic or overly promotional.

# MULTILINGUAL SUPPORT
Automatically detect language. Support English, Urdu, Arabic, Spanish, French, German, Hindi, and easily extendable. Reply in the customer's language whenever possible, with quality checks.

# FRONTEND
Create an extremely premium UI inspired by Stripe, Linear, OpenAI, Vercel, Notion, Framer, Apple.

# DESIGN STYLE
Minimal, Luxury, Modern, Glassmorphism, Soft Shadows, Rounded Components, Professional Typography, Micro Interactions, Premium Cards, Excellent Spacing, Responsive Design.

# COLOR THEME (unchanged)
Primary: Deep Indigo (#4F46E5), etc.

# ANIMATIONS (Framer Motion) — optimized for performance.

# RESPONSIVENESS — Perfect on Desktop, Tablet, Mobile.

# FRONTEND STACK (unchanged) — Next.js (App Router), React, TypeScript, Tailwind, shadcn/ui, etc.

# BACKEND
Python + FastAPI, OpenAI SDK, JWT, Async Architecture, Background Workers (Celery/Redis), PostgreSQL, SQLAlchemy, Alembic, Pydantic, Structured Logging, Rate Limiting, Caching, Multi-tenancy support.

# DATABASE
PostgreSQL with clear multi-tenant schema (Users, Businesses/Workspaces, Reviews, Replies, Platforms, Brand Settings, Knowledge Base, Embeddings, Activity Logs, API Keys, Usage Metrics, Audit Logs for compliance).

# API DESIGN (RESTful + OpenAPI/Swagger, versioning, validation, pagination, etc.)

# SECURITY (enhanced)
HTTPS, JWT + RBAC, Rate Limiting, Input/Output Sanitization, CORS, SQLi/XSS Protection, Secrets Management, Comprehensive Audit Logs, Data residency options.

# LOGGING & MONITORING
Structured JSON Logs (including AI decisions), Error Tracking, Latency, Token Usage, Prometheus metrics, Health Checks.

# AI OBSERVABILITY

Track detailed AI system metrics including:

- Prompt Version
- Model Version
- Embedding Model
- Token Usage
- Prompt Tokens
- Completion Tokens
- Estimated Cost
- Latency
- Embedding Time
- Retrieval Time
- Generation Time
- Evaluation Time
- Cache Hit Ratio
- Regeneration Count
- Human Override Rate
- Hallucination Rate
- Safety Violations
- AI Success Rate

Provide real-time dashboards and historical analytics for monitoring AI performance and operational costs.

# PERFORMANCE (unchanged + caching layers).

# QUEUE & EVENT-DRIVEN ARCHITECTURE

Design the application using an event-driven architecture.

**Workflow:**
```
Webhook
      │
      ▼
Message Queue
      │
      ▼
Review Processing Worker
      │
      ▼
AI Pipeline
      │
      ▼
Human Approval Queue
      │
      ▼
Publishing Worker
      │
      ▼
Analytics Worker
```

Implement:
- Celery Workers
- Redis Message Broker
- Retry Mechanisms
- Exponential Backoff
- Dead Letter Queue
- Priority Queues
- Scheduled Jobs
- Duplicate Detection
- Idempotent Processing

This architecture should ensure scalability, reliability, and fault tolerance.

# CACHING STRATEGY

Implement intelligent caching for:
- Embeddings
- Knowledge Base
- Business Profiles
- Prompt Templates
- Platform Configurations
- Recent AI Responses
- User Preferences
- Frequently Retrieved Documents

Use Redis to minimize latency and reduce LLM API costs.

# AI COST OPTIMIZATION

Optimize AI operational costs by implementing:
- Prompt Caching
- Embedding Caching
- Response Caching
- Batch Embedding Generation
- Token Budget Management
- Automatic Model Selection
- Streaming Responses
- Intelligent Retrieval Optimization
- Context Compression
- Dynamic Context Window Management

Use smaller models for simple tasks and automatically escalate to larger models for complex reviews when necessary.

# DEPLOYMENT
Docker, Docker Compose, CI/CD (GitHub Actions), Environment Variables, Blue-green deployments, Monitoring.

# TESTING (enhanced)
Unit, Integration, API, AI Prompt/Evaluation Tests (hallucination, tone, compliance), Security, Frontend, E2E, Load tests.

# PROJECT STRUCTURE (unchanged, but add compliance/audit modules).

# ENGINEERING STANDARDS

The entire project must follow modern software engineering best practices:

- Clean Architecture
- SOLID Principles
- Repository Pattern
- Dependency Injection
- Feature-Based Modules
- Async Programming
- Strict Type Safety
- Comprehensive Error Handling
- Environment Separation
- Conventional Commits
- Code Formatting
- Linting
- Modular Components
- Reusable Services
- High Test Coverage
- Comprehensive Documentation

# ADMIN DASHBOARD

Provide a comprehensive administrative dashboard including:

- User Management
- Workspace Management
- Tenant Management
- Prompt Management
- Prompt Versioning
- AI Model Configuration
- Guardrail Configuration
- API Key Management
- Platform Integrations
- Token Usage Analytics
- Billing Analytics
- Audit Logs
- Feature Flags
- System Health Dashboard
- AI Performance Metrics

# BUSINESS ANALYTICS

Provide advanced analytics including:

- AI Reply Acceptance Rate
- Human Edit Rate
- Average AI Quality Score
- Customer Sentiment Trends
- Average Response Time
- Platform-wise Performance
- Most Common Customer Complaints
- Top Performing Reply Templates
- Customer Satisfaction Trends
- Review Volume Analytics

# PROMPT VERSIONING

Support enterprise prompt lifecycle management including:

- Prompt Version Control
- A/B Testing
- Rollback Support
- Version History
- Draft & Production Environments
- Prompt Approval Workflow
- Prompt Performance Analytics

# FINAL REQUIREMENTS (Enhanced)
The finished application should:

- Feel like a premium enterprise SaaS product with strong compliance posture.
- Generate fast, context-aware, human-quality replies with mandatory safety layers.
- Use OpenAI SDK with robust RAG pipeline backed by vector database and hybrid search.
- Include enterprise-grade guardrails against prompt injection, hallucinations, toxicity, data leakage, and legal risks.
- Be modular, scalable, secure, observable, multi-tenant, and easy to maintain/extend.
- Deliver polished UX with modern animations while maintaining performance.
- Be production-ready, thoroughly documented (including compliance guides), and straightforward to extend with additional review platforms, AI models, and business-specific features.
- Include clear human oversight workflows, audit trails, and TOS compliance tooling to minimize business risk.

Loopholes Fixed & Improvements Made (without changing original structure):

- Added legal/compliance, human-in-the-loop, and risk indicators.
- Strengthened modularity, guardrails, multi-tenancy, and audit logging.
- Improved RAG/vector DB guidance and safety layers.
- Added TOS warnings and platform integration realism.
- Enhanced testing, security, and reliability sections.

# ACCEPTANCE CRITERIA

The final application will be considered production-ready only if it satisfies the following requirements.

## Functional Requirements

- Successfully integrate with all supported review platforms.
- Generate context-aware, on-brand AI replies.
- Enforce human approval for high-risk reviews.
- Block prompt injection and malicious inputs.
- Support multilingual responses.
- Maintain strict tenant isolation.
- Ensure reliable publishing workflows.
- Pass all automated AI evaluation checks before publishing.

## Non-Functional Requirements

- Enterprise-grade security.
- Horizontal scalability.
- High availability and fault tolerance.
- Average API response latency below acceptable production thresholds (excluding LLM inference).
- Complete audit logging.
- Comprehensive monitoring and observability.
- Optimized AI operational costs.
- Fully documented APIs, architecture, deployment procedures, and compliance guidelines.
- Maintainable, extensible, and production-ready codebase following modern engineering standards.
