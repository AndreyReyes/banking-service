# Milestones — TDD Checkpoints + Quality Gates

These milestones represent a checkpoint‑based delivery plan. Each checkpoint is a shippable slice validated by tests‑first and separated by a clean commit.

## Milestones (TDD + Commit Checkpoints)
Each checklist item is a shippable slice validated by tests‑first and separated by a clean commit.

### Project scaffolding & developer experience
- [x] Repo baseline (project scaffolding, lint/format, env config, CI/test runner)

### Production readiness foundations
- [x] Health and readiness endpoint (first running API)
- [x] Database wiring (SQLite) + migrations/init
- [x] Structured logging foundation (before auth)

### Core domain + business capabilities
- [x] Domain models + validation rules (no endpoints yet)
- [x] Signup (first real feature)
- [x] Authentication (login + token) + authentication middleware
- [x] Account holders CRUD (first protected resource)
- [x] Accounts (create + view + list)
- [x] Transactions (ledger entries + balance calculation)
- [x] Money transfer (the banking core)
- [x] Cards (minimal but real)
- [x] Statements (MVP version)

### Correctness & safety guarantees
- [x] Error handling production pass

### Operational deliverables
- [x] Containerization + env configs
- [x] Test coverage checkpoint (prove completeness)
- [x] Documentation + AI usage report
- [ ] Bonus demo flow integration test
- [ ] Bonus CLI demo client (interactive + config-driven)
- [ ] Bonus simple frontend interface

## How to read this plan
They’re a milestone‑based delivery plan + quality gates, broken into incremental TDD checkpoints.

More specifically, the checkpoints together encompass:

- **Project scaffolding & developer experience**: repo setup, lint/format, env config, CI
- **Production readiness foundations**: health/readiness checks, DB wiring, structured logging
- **Core domain + business capabilities**: users/signup/auth, account holders, accounts, transactions/ledger, transfers, cards, statements
- **Correctness & safety guarantees**: authz/ownership rules, validation, atomic transfers, error handling
- **Operational deliverables**: Docker/containerization, smoke tests, test coverage, documentation + AI usage report

So: end‑to‑end implementation plan for the assessment, where each checkpoint is a shippable slice validated by tests‑first and separated by clean commits.
