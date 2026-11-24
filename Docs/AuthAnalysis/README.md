| 📄 README | [Full Analysis](DCH_SO99_Authentication_Analysis.en.md) | [Executive Summary](DCH_SO99_Authentication_ExecutiveSummary.en.md) |
|:---:|:---:|:---:|

&nbsp;

# DCH & SO99+ — Authentication & Authorization Analysis

> **Two products, one identity strategy.**  
> This repository contains the complete analysis of authentication and authorization mechanisms across DCH (Demand Chain Hub) and SO99+ (Order Management), prepared for the Senior Director of Product Management.

---

## Why this exists

Authentication and authorization are strategic pillars. As DCH and SO99+ evolve — both independently and as part of the broader ToolsGroup platform — understanding how they handle identity today is essential to defining where we go tomorrow.

This analysis answers:

- 🔐 **How does each product authenticate users?** (SAML? Azure AD? Built-in?)
- 🛡️ **How does each product authorize actions?** (Roles? Permissions? Policies?)
- 🔗 **How do they communicate securely?** (API Keys? OAuth?)
- 🤝 **Can they align?** (What would it take? How much effort?)

---

## Available documents

| Document | Audience | Length | Best for |
|----------|----------|-------|----------|
| [📄 Full Analysis](DCH_SO99_Authentication_Analysis.en.md) | Technical & PM | ~20 pages | Deep dive, code references |
| [📄 Executive Summary](DCH_SO99_Authentication_ExecutiveSummary.en.md) | Senior Director | ~1 page | Meeting prep, quick read |

---

## Structure of the full analysis

1. **Executive Summary** — The one-slide overview
2. **General Architecture** — System landscape diagram
3. **Authentication in DCH** — SAML, OIDC, Windows, internal users
4. **Authorization in DCH** — Roles, permissions, filters
5. **Authentication in SO99+** — 6 modes, SO99PLUS, SAML, Azure AD, Auth0
6. **Authorization in SO99+** — WebClient & WebAPI, API Key, OAuth 2.0
7. **DCH ↔ SO99+ Communication** — How they talk to each other
8. **Comparison Tables** — Side-by-side across 20+ dimensions
9. **Integration Opportunities** — 5 concrete opportunities with priority
10. **Recommendations & Roadmap** — Short / Mid / Long term actions
11. **Appendix** — Key configuration files and source code references

---

## Key findings at a glance

| Statement | Status |
|-----------|--------|
| Both products use the same SAML 2.0 library (ComponentSpace) | ✅ |
| Both can share the same Azure AD as Identity Provider | ✅ |
| DCH has a more granular permission model than SO99+ | ✅ |
| Neither maps Azure AD groups to application roles | ⚠️ Gap |

---

## Files in this folder

```
AuthAnalysis/
├── README.md                                   ← This file
├── DCH_SO99_Authentication_Analysis.en.md       ← Full analysis (EN)
└── DCH_SO99_Authentication_ExecutiveSummary.en.md ← Executive summary (EN)
```

---

*Analysis generated from source code — DCH (ASP.NET 4.8 / VB.NET + C#) and SO99+ (.NET Core 8 / C#). November 2026.*