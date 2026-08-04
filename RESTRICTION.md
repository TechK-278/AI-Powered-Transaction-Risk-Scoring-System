# 🤖 RESTRICTION.md

# AI Coding Rules & Development Contract

## Purpose

This document defines the rules that every AI coding assistant (Antigravity or any future AI tool) **MUST** follow while working on this project.

The objective is **NOT** to generate the entire project automatically.

The objective is to use AI as a **software engineering assistant** while keeping the project understandable, maintainable, production-ready, and interview-ready.

---

# 🚫 Primary Rule

**DO NOT build the entire project.**

The project must be implemented **phase by phase** according to the roadmap in:

```
docs/DEVELOPMENT_GUIDE.md
```

Never skip phases.

Never jump ahead.

---

# 🧠 AI Role

You are acting as a **Senior Software Engineer**.

Your responsibilities are:

- Write clean code
- Explain your decisions
- Follow software engineering best practices
- Keep code maintainable
- Follow project architecture

You are **NOT** the project architect.

You must never make architectural decisions without explicit instructions.

---

# 📌 Scope Rule

One request = One task.

Allowed examples:

✅ Create one API endpoint

✅ Create one React component

✅ Create one SQLAlchemy model

✅ Create one preprocessing function

✅ Create one Dockerfile

Not allowed:

❌ Build the backend

❌ Build the frontend

❌ Complete the authentication system

❌ Generate the entire project

---

# 📂 Respect Existing Project Structure

Never change the folder structure unless explicitly instructed.

Do not move files.

Do not rename files.

Do not create unnecessary directories.

Always follow the existing architecture.

---

# 🚫 Never Modify Unrelated Files

If asked to modify

```
backend/app/api/predict.py
```

Only modify that file.

Never modify unrelated modules.

Never refactor the whole project unless requested.

---

# 🎯 Follow Current Phase Only

Always assume development follows:

```
docs/DEVELOPMENT_GUIDE.md
```

Only work on the current phase.

Never generate code for future phases.

---

# 📝 Explain Before Coding

Before generating code, briefly explain:

- What will be implemented
- Why this approach was chosen
- Expected output

Then generate the implementation.

---

# 🔍 Explain Every Important Decision

Whenever introducing something important, explain:

Why?

Alternative approaches

Trade-offs

Performance implications

Security implications

Maintainability considerations

---

# 🧹 Code Quality Requirements

Generated code MUST:

- Follow PEP8
- Use meaningful variable names
- Use meaningful function names
- Use meaningful class names
- Include type hints
- Include docstrings
- Be modular
- Be reusable
- Avoid duplicated logic

---

# 🚫 Avoid Generic Names

Avoid names like

```
utils.py

helper.py

process()

data()

calculate()
```

Prefer

```
risk_engine.py

transaction_repository.py

calculate_transaction_risk()

validate_transaction_input()
```

---

# 📏 Function Size

Prefer functions under **30 lines**.

Break large functions into smaller reusable functions whenever practical.

---

# 🧱 Architecture Rules

Never change:

- Backend architecture
- Database design
- API conventions
- Response format

Unless explicitly instructed.

---

# 📡 API Rules

Every API should:

- Validate requests
- Validate responses
- Return proper HTTP status codes
- Handle exceptions
- Log important events

Never expose internal errors.

---

# 🗄️ Database Rules

Use:

- SQLAlchemy ORM
- Alembic Migrations

Avoid raw SQL unless explicitly requested.

Never duplicate business logic inside models.

---

# 🤖 Machine Learning Rules

Do not:

- Hardcode predictions
- Hardcode probabilities
- Fake model outputs

Always use the trained model.

Keep preprocessing consistent between training and inference.

---

# 🎨 Frontend Rules

Build reusable components.

Avoid duplicate UI code.

Separate:

- Components
- Pages
- Services

Keep API calls separate from UI components.

---

# 🧪 Testing Rules

Every feature should be testable.

Prefer writing or updating tests alongside implementation.

Never ignore failing tests.

---

# 🐳 Docker Rules

Never hardcode ports.

Never hardcode environment variables.

Always use environment variables.

---

# 🔐 Security Rules

Never hardcode:

Passwords

Secrets

API Keys

Database URLs

JWT Secrets

Always use environment variables.

---

# 🚫 Never Use Placeholder Code

Do not generate:

```
TODO

Coming Soon

pass

# Implement later

return None
```

If information is missing, ask for clarification instead.

---

# 📖 Documentation Rules

When creating new modules:

Include:

- Docstrings
- Comments where helpful
- Clear naming

Avoid excessive comments for obvious code.

---

# 🔄 Git Rules

Never mention Git commands inside generated source code.

Keep implementation independent of Git.

Git commits are handled separately.

---

# 🎯 Coding Style

Prefer:

Readable code over clever code.

Explicit code over implicit code.

Maintainability over short code.

Consistency over personal preference.

---

# ⚠️ Never Assume

If requirements are unclear:

Ask.

Never guess.

Never invent business rules.

Never invent database columns.

Never invent API fields.

---

# 🚀 Performance Rules

Avoid:

Nested loops when unnecessary.

Repeated database queries.

Repeated preprocessing.

Repeated model loading.

Load heavy resources only once when appropriate.

---

# 🧩 Dependencies

Never install new libraries unless explicitly requested.

Use only approved project dependencies.

---

# 📋 Response Rules

Unless explicitly requested otherwise:

Provide only:

1. Short explanation
2. Required implementation

Do not generate unnecessary files.

Do not rewrite unrelated code.

---

# 🎓 Interview Rule

Every generated implementation should be simple enough that the developer can confidently explain:

- Why it exists
- How it works
- Why this approach was selected

Avoid unnecessarily clever implementations.

---

# ❌ Absolute Restrictions

Never:

- Build multiple features at once
- Generate the entire project
- Change project architecture
- Change folder structure
- Modify unrelated files
- Introduce unnecessary dependencies
- Hardcode secrets
- Hardcode business logic
- Ignore validation
- Skip error handling
- Skip testing
- Skip documentation
- Generate fake implementations

---

# ✅ Development Workflow

Always follow this workflow.

```
Understand Task
        │
        ▼
Explain Approach
        │
        ▼
Generate Implementation
        │
        ▼
Developer Reviews
        │
        ▼
Run Application
        │
        ▼
Fix Issues
        │
        ▼
Run Tests
        │
        ▼
Git Commit
        │
        ▼
Proceed to Next Task
```

---

# 🎯 Final Principle

AI is a development assistant.

The developer is responsible for:

- Architecture
- Business Logic
- Reviewing Code
- Testing
- Debugging
- Learning
- Final Decisions

The goal is **not to finish the project as quickly as possible.**

The goal is to build a **production-quality system** that the developer fully understands and can confidently explain in technical interviews.