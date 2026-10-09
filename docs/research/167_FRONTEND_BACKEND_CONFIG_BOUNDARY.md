# CLINOVA AI — Frontend vs. Backend Configuration Boundary & Styling System

> **Document ID:** `RES-167`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Frontend Architecture, Systems Security & Clinical Design Group  

---

## 1. Architectural Boundary Isolation Law

In modern Next.js and single-page web architectures, the compile-time inlining of environment variables poses an extreme vulnerability vector: developers frequently expose sensitive server secrets by inadvertently referencing them in client-rendered components or prepending `NEXT_PUBLIC_` to internal variables.

**The Inviolable Boundary Law:**
$$\mathbf{Client\ Bundle} \cap \mathbf{Server\ Secrets} = \emptyset$$

1. **Frontend (Browser Runtime):** Operates under a Zero-Trust assumption. It holds zero database credentials, zero service-role keys, and zero signing secrets. Every client request to the backend must be accompanied by an ephemeral, cryptographically verified user session token.
2. **Backend (FastAPI Runtime):** Authoritative custodian of all clinical invariants, database persistence pools, storage drivers, cryptographic HMAC keys, and audit ledgers.

---

## 2. Next.js Public vs. Server-Only Variable Boundary

Next.js App Router enforces two execution environments: Node.js/Edge Server vs. Client Web Browser.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       NEXT.JS CONFIGURATION BOUNDARY                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ SERVER-SIDE ENVIRONMENT (Node.js Process) ]                              │
│  ├── Access to private variables: SECRET_KEY, DATABASE_URL, etc.            │
│  ├── Server Components (`page.tsx`, `layout.tsx` without "use client")      │
│  ├── Route Handlers (`app/api/*/route.ts`)                                  │
│  └── NEVER leaks to client bundles unless explicitly passed via props.      │
│                                                                             │
│         │ Props Serialization Barrier (JSON Sanitization)                   │
│         ▼                                                                   │
│  [ CLIENT-SIDE ENVIRONMENT (Browser Engine) ]                               │
│  ├── Inlined at Webpack/Turbopack build time via `NEXT_PUBLIC_*` prefix     │
│  ├── Client Components ("use client")                                       │
│  └── Completely visible in plain text via DevTools / Page Source.           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Approved `NEXT_PUBLIC_*` Variables
Only seven variables are permitted to carry the `NEXT_PUBLIC_` prefix:
1. `NEXT_PUBLIC_APP_ENV`: Tells the UI which environment banner to render.
2. `NEXT_PUBLIC_CLINOVA_ENVIRONMENT_ID`: Configures facility-specific UI labels and queue modes.
3. `NEXT_PUBLIC_API_URL`: Backend endpoint address for fetch requests.
4. `NEXT_PUBLIC_APP_NAME`: Display branding.
5. `NEXT_PUBLIC_VERSION`: Version footer string.
6. `NEXT_PUBLIC_DATA_MODE`: Renders the prominent "SYNTHETIC DEMO" or "LIVE RECORD" indicator.
7. `NEXT_PUBLIC_OFFLINE_MODE`: Activates offline client cache visual badges.

### Explicitly Forbidden `NEXT_PUBLIC_*` Names
Automated CI/CD lint rules reject any variable matching:
- `NEXT_PUBLIC_*SERVICE_ROLE*`
- `NEXT_PUBLIC_*SECRET*`
- `NEXT_PUBLIC_*PASSWORD*`
- `NEXT_PUBLIC_*PRIVATE*`
- `NEXT_PUBLIC_*TOKEN*` (except Supabase Anon token when explicitly in cloud mode)
- `NEXT_PUBLIC_DATABASE_URL`

---

## 3. Frontend Technology Correction: Rejection of Tailwind CSS

### 3.1 Architectural Rationale for Rejection
Phase 8 documentation noted Tailwind CSS as the styling framework. This is **formally rejected** in Phase 9 for four critical reasons:
1. **Clinical Design System Rigidity:** Healthcare clinical workstations require strict, unpolluted design tokens for triage acuity (Red/Amber/Yellow/Blue/Green), high contrast readability under harsh fluorescent hospital lighting, and touch-target sizing ($\ge 48\text{px}$). Utility classes invite arbitrary styling drift across team members.
2. **Bundle Overhead & Build Dependency:** Removing Tailwind eliminates PostCSS generation passes, arbitrary-value compilation, and external runtime dependencies, aligning directly with Phase 8's Zero-Cost and Lightweight Edge mandates.
3. **Pure Web Standards Alignment:** Native CSS Custom Properties (CSS variables) supported in all modern browsers provide zero-runtime dynamic theming, instant dark/light/high-contrast mode switching, and native scoping via CSS Modules (`*.module.css`).
4. **Long-Term Maintainability:** Clinical software must be auditable and maintainable over 10–15 year hospital operational lifecycles without framework churn.

### 3.2 Approved Styling Stack: Plain CSS & Design Token Specification
The CLINOVA AI frontend styling architecture consists of:
- **Core Engine:** Plain CSS with native CSS Modules (`component.module.css`).
- **Layout:** Native CSS Grid and Flexbox for responsive, dense clinical tables and split-screen verification views.
- **Tokens:** Centralized CSS Custom Properties defined in `frontend/src/app/globals.css`.
- **Icons:** `lucide-react` (clean, un-opinionated SVG symbols; no decorative emojis).

#### Canonical Clinical Design Tokens (`globals.css`)
```css
:root {
  /* Surface & Slate Backgrounds */
  --color-surface-bg: #f8fafc;        /* slate-50 */
  --color-surface-card: #ffffff;      /* white */
  --color-surface-border: #e2e8f0;    /* slate-200 */
  --color-surface-hover: #f1f5f9;     /* slate-100 */

  /* Text & Contrast */
  --color-text-primary: #0f172a;     /* slate-900 (High contrast) */
  --color-text-secondary: #475569;   /* slate-600 */
  --color-text-muted: #94a3b8;       /* slate-400 */

  /* Clinical Acuity Tiers (Standardized Emergency Colors) */
  --color-acuity-critical-bg: #fef2f2;   /* Red-50 */
  --color-acuity-critical-text: #991b1b; /* Red-800 */
  --color-acuity-critical-border: #dc2626;/* Red-600 */

  --color-acuity-urgent-bg: #fffbeb;     /* Amber-50 */
  --color-acuity-urgent-text: #92400e;   /* Amber-800 */
  --color-acuity-urgent-border: #d97706; /* Amber-600 */

  --color-acuity-moderate-bg: #fefce8;   /* Yellow-50 */
  --color-acuity-moderate-text: #854d0e; /* Yellow-800 */
  --color-acuity-moderate-border: #ca8a04;/* Yellow-600 */

  --color-acuity-routine-bg: #f0fdf4;    /* Green-50 */
  --color-acuity-routine-text: #166534;  /* Green-800 */
  --color-acuity-routine-border: #16a34a;/* Green-600 */

  /* Clinical Interactive Brand */
  --color-brand-primary: #0284c7;        /* Sky-600 */
  --color-brand-primary-hover: #0369a1;  /* Sky-700 */
  --color-brand-accent: #0f766e;         /* Teal-700 */

  /* Spatial Grid & Touch Targets */
  --touch-target-min: 48px;
  --spacing-unit: 8px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Typography */
  --font-clinical-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  --font-clinical-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}
```

---

## 4. Frontend Data Hydration & Server Component Boundaries

1. **Root Layout (`layout.tsx`):**
   - Renders as a Next.js Server Component.
   - Ingests public configuration and renders the persistent Non-Diagnostic Safety Header and the Environment Banner.
   - Never queries the database directly; delegates data fetching to Backend REST endpoints.
2. **Interactive Clinical Workbenches (`doctor/[caseId]/page.tsx`):**
   - Marked with `"use client"`.
   - Hydrates state via JSON fetch calls to `NEXT_PUBLIC_API_URL`.
   - Receives zero backend secrets; validates session tokens on every interaction.
   - Renders side-by-side verification crops using pure CSS Grid (`display: grid; grid-template-columns: 1fr 1fr; gap: 16px;`).
