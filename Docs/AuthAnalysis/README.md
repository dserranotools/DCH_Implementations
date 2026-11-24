| [Technical Analysis](DCH_SO99_Authentication_Analysis.en.md) | [Executive Summary](DCH_SO99_Authentication_ExecutiveSummary.en.md) | 📄 README |
|:---:|:---:|:---:|

&nbsp;

# DCH & SO99+ — Authentication & Authorization Analysis

Analysis of how **DCH (Demand Collaboration Hub)** and **SO99+** authenticate users and authorize their actions, and how both products can be aligned. Prepared for the meeting with the Senior Director, Product Management.

All statements are based on the source code and configuration of DCH 4.40 and SO99+ 2026.3.

---

## Documents

| Document | Audience | Length |
|---|---|---|
| [Executive Summary](DCH_SO99_Authentication_ExecutiveSummary.en.md) | Product Management | ~2 pages |
| [Technical Analysis](DCH_SO99_Authentication_Analysis.en.md) | Technical & Product | ~10 pages |

**Recommended reading:** start with the Executive Summary; use the Technical Analysis for details.

---

## Questions answered

- 🔐 How does each product authenticate users?
- 🛡️ How does each product authorize actions and data access?
- 🔗 How are DCH and SO99+ connected today?
- 🤝 Which parts are compatible, which are not, and what integration is possible?

---

## Key findings

| Finding | |
|---|:---:|
| Both products follow the same pattern: the IdP identifies, the application authorizes against its own users | 🟢 |
| Both support SAML 2.0 (same library), Azure AD, and Windows authentication | 🟢 |
| The same identity provider can serve both products today, through configuration | 🟢 |
| Users are registered separately in each product | 🟡 |
| Role and permission models are different and have no direct equivalence | 🔴 |
| DCH reads SO99+ data directly from its database; there is no shared session or user store | ℹ️ |

---

## Folder contents

```
AuthAnalysis/
├── README.md
├── DCH_SO99_Authentication_ExecutiveSummary.en.md   ← Executive summary (EN)
└── DCH_SO99_Authentication_Analysis.en.md           ← Technical analysis (EN)
```
