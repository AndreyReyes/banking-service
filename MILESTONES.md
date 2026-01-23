# Milestones — TDD Checkpoints + Quality Gates

These milestones represent a checkpoint‑based delivery plan. Each checkpoint is a shippable slice validated by tests‑first and separated by a clean commit.

## Milestones (TDD + Commit Checkpoints)
Each checklist item is a shippable slice validated by tests‑first and separated by a clean commit.

### Project scaffolding & developer experience
- [x] Repo baseline (project scaffolding, lint/format, env config, CI/test runner)

### Production readiness foundations
- [ ] Health and readiness endpoint (first running API)
- [ ] Database wiring (SQLite) + migrations/init
- [ ] Structured logging foundation (before auth)

### Core domain + business capabilities
- [ ] Domain models + validation rules (no endpoints yet)
- [ ] Signup (first real feature)
- [ ] Authentication (login + token) + authentication middleware
- [ ] Account holders CRUD (first protected resource)
- [ ] Accounts (create + view + list)
- [ ] Transactions (ledger entries + balance calculation)
- [ ] Money transfer (the banking core)
- [ ] Cards (minimal but real)
- [ ] Statements (MVP version)

### Correctness & safety guarantees
- [ ] Error handling production pass

### Operational deliverables
- [ ] Containerization + env configs
- [ ] Test coverage checkpoint (prove completeness)
- [ ] Documentation + AI usage report

## How to read this plan
They’re a milestone‑based delivery plan + quality gates, broken into incremental TDD checkpoints.

More specifically, the checkpoints together encompass:

- **Project scaffolding & developer experience**: repo setup, lint/format, env config, CI
- **Production readiness foundations**: health/readiness checks, DB wiring, structured logging
- **Core domain + business capabilities**: users/signup/auth, account holders, accounts, transactions/ledger, transfers, cards, statements
- **Correctness & safety guarantees**: authz/ownership rules, validation, atomic transfers, error handling
- **Operational deliverables**: Docker/containerization, smoke tests, test coverage, documentation + AI usage report

So: end‑to‑end implementation plan for the assessment, where each checkpoint is a shippable slice validated by tests‑first and separated by clean commits.
