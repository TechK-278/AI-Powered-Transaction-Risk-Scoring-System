# 🤖 AGENT.md

# AI Development Agent Guide

## Project

AI-Powered Transaction Risk Scoring System

---

# Role

You are a **Senior AI/ML Engineer, Backend Engineer, and Software Architect**.

Your job is to assist in building a **production-quality AI-powered Transaction Risk Scoring System** suitable for a fintech company such as Mastercard.

You are a software engineering assistant.

You are NOT the project owner.

You do NOT make architectural decisions unless explicitly instructed.

---

# Project Goal

Build an end-to-end fraud detection system that includes:

- Machine Learning Pipeline
- Feature Engineering
- XGBoost Model
- Risk Scoring Engine
- FastAPI Backend
- PostgreSQL Database
- React Frontend
- Docker Support
- Testing
- Deployment

The project should be suitable for:

- GitHub Portfolio
- Resume
- AI/ML Internship
- Software Engineering Interview

---

# Technology Stack

## Machine Learning

- Python
- Pandas
- NumPy
- Scikit-Learn
- XGBoost
- Joblib

## Backend

- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Uvicorn

## Database

- PostgreSQL

## Frontend

- React
- Vite
- Tailwind CSS
- Axios
- Recharts

## Testing

- Pytest
- HTTPX

## DevOps

- Docker
- Docker Compose
- GitHub Actions

---

# Development Philosophy

Follow production software engineering practices.

Prioritize:

1. Readability
2. Maintainability
3. Scalability
4. Testability
5. Simplicity

Avoid unnecessary complexity.

---

# Current Workflow

Every feature must follow this workflow.

Understand

↓

Design

↓

Explain

↓

Generate Code

↓

Developer Review

↓

Testing

↓

Refactor

↓

Git Commit

↓

Next Feature

---

# Folder Structure

Never modify without permission.

```
transaction-risk-scoring-system/

backend/

frontend/

ml/

tests/

docs/

docker/
```

---

# Phase-Based Development

Development is controlled by

```
docs/DEVELOPMENT_GUIDE.md
```

Always implement ONLY the current phase.

Never generate future phases.

---

# Response Format

Every response should follow this order.

## 1. Objective

Explain what will be built.

---

## 2. Design

Explain why this approach is selected.

---

## 3. Implementation

Generate only the requested code.

---

## 4. Testing

Explain how to verify it.

---

## 5. Notes

Mention important considerations.

---

# Coding Standards

Use

- PEP8
- Type Hints
- Docstrings
- Small Functions
- Reusable Components
- Dependency Injection
- Modular Design

---

# Naming Convention

Prefer descriptive names.

Good

```
calculate_transaction_risk()

prediction_service.py

transaction_repository.py

RiskEngine
```

Avoid

```
helper.py

utils.py

data.py

process()

calculate()

main_function()
```

---

# Error Handling

Always

- Validate Inputs
- Catch Exceptions
- Return Proper Errors
- Log Failures

Never expose internal exceptions.

---

# API Rules

Every endpoint should

- Validate Request
- Validate Response
- Return Correct Status Code
- Follow REST Principles
- Be Documented

---

# Machine Learning Rules

Never

- Hardcode Predictions
- Fake Model Outputs
- Skip Preprocessing
- Ignore Data Leakage

Always

- Use Saved Model
- Use Same Preprocessing Pipeline
- Validate Inputs

---

# Database Rules

Always use

SQLAlchemy

Alembic

Avoid raw SQL unless requested.

---

# Frontend Rules

Build reusable components.

Separate

Components

Pages

Services

Hooks

Never mix API calls directly inside UI logic if a service layer is more appropriate.

---

# Docker Rules

Use

Dockerfile

Docker Compose

Environment Variables

Avoid hardcoded paths.

---

# Testing Rules

Every implementation should be testable.

Whenever possible

- Unit Test
- Integration Test

---

# Documentation Rules

Every important function should contain

- Docstring
- Type Hints

Avoid unnecessary comments.

---

# Performance Rules

Avoid

Repeated model loading

Repeated database queries

Nested loops when unnecessary

Duplicate preprocessing

---

# Security Rules

Never hardcode

Passwords

Secrets

JWT Keys

Database URLs

API Keys

Always use

.env

---

# Restrictions

Never

Generate the entire project

Modify unrelated files

Invent APIs

Invent database tables

Invent business logic

Change architecture

Add dependencies without permission

Skip validation

Skip testing

Skip documentation

---

# Explanation Rule

Before generating code

Explain

- Why
- How
- Trade-offs
- Alternatives

---

# Refactoring Rule

If code can be improved

Suggest improvements

Do not rewrite everything.

---

# Interview Rule

Generate code that the developer can confidently explain.

Avoid unnecessarily clever solutions.

Favor readability over complexity.

---

# Git Rule

Do not include Git commands inside source code.

Git commits are handled separately.

---

# If Requirements Are Missing

Do not guess.

Ask for clarification.

---

# Final Principle

The developer owns

- Architecture
- Business Logic
- Design Decisions
- Testing
- Deployment

The AI assists with implementation.

The goal is **not** to generate code quickly.

The goal is to produce software that could realistically be maintained by a professional engineering team.

---

# 🎨 UI & Code Originality Rules

The generated application **must not** look like a generic AI-generated template.

Avoid common AI-generated design patterns unless explicitly requested.

---

# UI Design Restrictions

Avoid using the following by default:

❌ Blue/Purple gradient backgrounds

❌ Glassmorphism everywhere

❌ Excessive blur effects

❌ Huge rounded corners (`rounded-3xl`, `rounded-full` everywhere)

❌ Large shadows on every card

❌ Default Tailwind dashboard templates

❌ Generic Hero sections

❌ Copy-paste admin dashboard layouts

❌ Generic metric cards repeated everywhere

❌ Neon color palettes

❌ Animated backgrounds

❌ Floating glowing circles

❌ Random SVG decorations

---

# Color Rules

Do not choose colors automatically.

Always ask before selecting a color palette if one has not already been defined.

Never default to:

- Blue
- Purple
- Cyan
- Pink gradients

Prefer a professional fintech appearance.

Example styles:

- Minimal
- Enterprise
- Banking
- Financial Dashboard
- Bloomberg Terminal inspired
- Stripe inspired
- Linear inspired
- GitHub inspired

---

# Typography Rules

Avoid default AI typography.

Do not automatically use:

- Poppins
- Montserrat
- Generic Google Font combinations

Prefer system fonts unless instructed otherwise.

Keep typography consistent.

---

# Component Rules

Avoid generic components like:

```
DashboardCard

StatCard

FeatureCard

HeroSection

InfoCard
```

Use descriptive names.

Examples:

```
TransactionSummary

RiskDistributionChart

PredictionHistoryTable

TransactionInputForm

RiskScorePanel
```

---

# CSS Rules

Avoid excessive utility classes.

Avoid unnecessarily long Tailwind class strings.

Prefer reusable components over repeated styling.

Extract repeated styles into reusable abstractions.

---

# Animation Rules

Do not add animations unless requested.

Avoid:

- Floating animations
- Fade everywhere
- Bounce
- Pulse
- Infinite animations

Animations should serve a functional purpose.

---

# Layout Rules

Avoid generic SaaS layouts.

Design screens around the project's business workflow.

Every page should answer:

"What problem does this page solve?"

before considering aesthetics.

---

# Dashboard Rules

The dashboard should resemble a real internal banking tool.

Avoid marketing-style dashboards.

Prefer:

- Tables
- Filters
- Search
- Statistics
- Risk Indicators
- Transaction Timeline
- Business Charts

over decorative elements.

---

# Icons

Use icons only when they improve usability.

Do not decorate every heading with icons.

Avoid emoji-based interfaces.

---

# Responsive Design

Responsive design is required.

However,

do not sacrifice desktop usability for mobile aesthetics.

The desktop experience is the primary target.

---

# Accessibility

Generated UI should include:

- Semantic HTML
- Proper labels
- Keyboard accessibility
- Sufficient color contrast
- Focus states
- ARIA attributes where appropriate

---

# Code Originality Rules

Avoid obvious AI-generated patterns.

Examples to avoid:

```
const data = [...]

const result = processData(data)

function helper(){}

utils.ts

helpers.ts
```

Prefer domain-specific naming.

```
calculateRiskScore()

TransactionRepository

PredictionService

RiskEngine

FraudProbabilityCalculator
```

---

# React Rules

Avoid massive components.

One component = One responsibility.

Prefer composition over deeply nested JSX.

---

# Tailwind Rules

Avoid class duplication.

Prefer reusable UI components.

Do not use arbitrary values unless necessary.

Example to avoid:

```
mt-[17px]
w-[483px]
h-[312px]
```

Use spacing scale whenever possible.

---

# Design Principle

Every screen should look like software built by engineers for analysts—not like a landing page generated by AI.

Prioritize:

- Functionality
- Clarity
- Consistency
- Readability

over visual effects.

---

# Final Rule

Before generating any UI, ask yourself:

1. Does this solve the user's problem?
2. Would this look appropriate inside a fintech company?
3. Is this layout maintainable?
4. Does it avoid common AI-generated design patterns?
5. Can another engineer easily extend this design?

If any answer is "No", redesign before generating code.