# AI Usage Report

This report summarizes how AI was used to deliver the banking service, with an
emphasis on production readiness, testing, and operational concerns. It also
maps the requested deliverables to the current implementation and documents
evidence sources (docs, code, tests, AI logs, and transcripts).

## AI usage approach

- Google Gemini was used to learn about AI tools and their usage, for example,
  Cursor workflows and approaches to reinforce a Test-Driven Development (TDD)
  environment. The main takeaways from Gemini were:
    - To focus on segregation and TDD in a way that allowed me to both
      understand and double-check what was being developed.
    - To have enough granularity to guide the tools toward the desired result,
      achieving this by fully defining the architecture and requirements in a
      stage-by-stage approach.
    - To enforce segregation to validate completeness and fully functional code
      and processes by intentionally using a new agent per phase, breaking any
      previous knowledge aside from what was documented.
- Primary tool: Cursor AI agents to plan and implement each phase in small,
  test-first increments (see `AI_LOG.md` and `ai_chats/` transcripts).
- The strategy was:
    - To have an agent digest the homework instructions in
      `FDE_Tech_Assessment_(T2).md` and then, through conversations, guide it to
      produce `TECHNICAL_SPEC.md`, which in turn was used the same way to create
      `MILESTONES.md` and `ARCHITECTURE.md`, then repeat the process to create
      `IMPLEMENTATION_PLAN.md`.
    - The same process in the previous bullet was used to create the git
      workflow guidelines and Cursor rules.
    - To build `IMPLEMENTATION_PLAN.md` in such a way that it had clear
      test-first executable steps called "phases" so that these map to the
      items in `MILESTONES.md`, which in turn was derived from the interpretation
      of `FDE_Tech_Assessment_(T2).md`.
    - To instruct an agent to implement a phase in `IMPLEMENTATION_PLAN.md` by
      following TDD-first (red/green/refactor), strict milestone gates, git
      workflows, and Cursor guardrails established in the project .md/.txt files
      and Cursor rules.
    - To have different agents implement each "phase" sequentially after full,
      successful TDD completion of the previous stage.
    - To instruct each agent to document in `AI_LOG.md` how AI was used to
      develop each phase and any issues encountered. Note that each section in
      `AI_LOG.md` has the name of the title of the chat with the agent.
    - Example of a prompt:
    ```
    Phase 5 of the implementation plan. Following the guides defined in @ARCHITECTURE.md   and @IMPLEMENTATION_PLAN.md, and with the help of the @README.md  and any other .txt and .md  files at the root directory, do regresion testing and if successful , then start implementation of Phase 5: Operational deliverables.  Once done we should be able to check one or some items in @MILESTONES.md . Please use the pre stablished TDD approach and document the process by appending at the end of the file @AI_LOG.md . Follow any guidelines defined in @.cursor/rules .
    As you go, keep track of everything that's done so that at the very end once the tests for phase 5 pass, you can summarize my prompts and iterations in this chat, how AI was used, the challenges encountered and how they were solved, any manual intervention I had to do, and the things achieved. Those are to be documented by appending them at the end to file @AI_LOG.md . Use markup and create a new subsection under  '# AI Usage Log' and name it 'Phase 5: Operational deliverables' and organize the summary under it.
    ```

## Deliverables mapped to requested items (AI usage focus)

### Idempotency and atomicity

- Atomicity is enforced via a single SQLAlchemy session commit/rollback per
  request, with explicit nested transactions for transfers. This ensures that
  multi-step transfer operations either fully succeed or roll back.
```53:61:app/db/session.py
def get_db() -> Generator[Session, None, None]:
    SessionLocal = get_sessionmaker()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
```
```16:39:app/api/routes/transfers.py
@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransferRead)
def create_transfer(
    payload: TransferCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TransferRead:
    # ...
    try:
        with session.begin_nested():
            transfer = service.transfer(
                current_user,
                from_account,
                to_account,
                payload.amount,
                payload.currency,
            )
```
- Idempotency keys are not implemented; repeated requests will create duplicate
  transactions. This is a known gap and a future improvement area (can be added
  via idempotency tokens and request de-duplication in the service layer).

### Containerization

- Multi-stage Docker build and docker-compose configuration are implemented,
  and validated via integration tests.
```14:23:tests/integration/test_containerization.py
def test_dockerfile_is_multistage() -> None:
    assert DOCKERFILE_PATH.exists(), "Dockerfile is missing"
    contents = DOCKERFILE_PATH.read_text(encoding="utf-8")
    from_lines = [
        line for line in contents.splitlines() if line.strip().lower().startswith("from ")
    ]
    assert len(from_lines) >= 2, "Dockerfile should use multi-stage builds"
    assert "as builder" in contents.lower(), "Dockerfile should include a builder stage"
    assert "as runtime" in contents.lower(), "Dockerfile should include a runtime stage"
```
- Deployment blueprint and production environment variables are documented in
  `render.yaml` and `README.md`.

### Test suite and test practices

- Tests are split into unit and integration coverage under `tests/`.
- TDD is documented and enforced as process in `AI_LOG.md`.
- Coverage is enforced at 92% via `pytest-cov` (see `README.md`,
  `requirements-dev.txt`, and `pyproject.toml`).
- Container tests are optional and gated by `RUN_DOCKER_TESTS=1`.

### Security considerations

- Password hashing uses bcrypt, JWT access tokens, refresh token rotation, and
  audit logging; production env enforces non-default `JWT_SECRET`.
- Security posture and secret handling are documented in `SECURITY.md` and
  enforced in configuration.
```7:34:app/core/config.py
class AppSettings(BaseSettings):
    app_env: str = "dev"
    database_url: str = "sqlite:///./banking.db"
    log_level: str = "INFO"
    auto_migrate: bool = False
    jwt_secret: str = "dev_insecure_secret_change_me"
    # ...
    @model_validator(mode="after")
    def validate_jwt_secret(self) -> "AppSettings":
        env = self.app_env.lower()
        if env in {"prod", "production"}:
            if self.jwt_secret == "dev_insecure_secret_change_me":
                raise ValueError("jwt_secret must be set in production")
            if self.auto_migrate:
                raise ValueError("auto_migrate must be disabled in production")
```

### Logging and log levels

- Structured JSON logging is implemented via structlog and request middleware.
```8:24:app/core/logging.py
def configure_logging(log_level: str = "INFO") -> None:
    resolved_level = logging._nameToLevel.get(log_level.upper(), logging.INFO)
    logging.basicConfig(level=resolved_level, format="%(message)s")
    structlog.configure(
        processors=[
            merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(resolved_level),
        cache_logger_on_first_use=True,
    )
```
```14:47:app/core/middleware.py
        request_id = request.headers.get("X-Request-Id") or str(uuid4())
        bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        # ...
        self._logger.info(
            "request.completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
```
- Logging behavior is validated via `tests/integration/test_logging.py`.

### API documentation

- FastAPI interactive docs are exposed at `/docs` and `/openapi.json`.
- Static API reference is in `API.md` and supported by `TECHNICAL_SPEC.md`.

### Setup instructions and deployment guide

- Local setup and environment variables are documented in `README.md`.
- `scripts/setup_env.sh` bootstraps a venv and installs dev dependencies.
- Render deployment is documented in `README.md` and configured in `render.yaml`.

### Production readiness and operational concerns

- Health checks and DB connectivity gating (`/v1/health` and startup checks)
  are implemented and tested (`tests/integration/test_health.py`).
- SQLite is configured with WAL and busy timeout for safer concurrency.
- CI (`.github/workflows/ci.yml`) enforces lint + tests on push/PR.
- Docker healthcheck is built into Dockerfile and compose.

### Environment handling and CI differences

- Env vars are documented in `README.md` and validated in `app/core/config.py`.
- Dev defaults: `APP_ENV` defaults to `dev`, `AUTO_MIGRATE=true` when unset.
- Test suite uses dedicated sqlite DBs and explicit env overrides in fixtures.
- Production: `AUTO_MIGRATE=false`, `JWT_SECRET` must be non-default.
- CI uses `requirements-dev.txt` and defaults unless test fixtures override.

### Future considerations

See `ROADMAP.md` for planned follow-ups, including error envelope coverage
expansion and other operational improvements.

## AI usage evidence (prompts, iterations, challenges)

### Example prompt categories (from `ai_chats/` and transcripts)

- Phase-by-phase implementation instructions with TDD constraints.
- Requests for architectural planning and spec refinement.
- Deployment and operational questions (Render, Docker, CI/CD).
- Documentation gaps: API docs, workflow docs, and security clarifications.

### Challenges and AI-assisted solutions

- Test environment bootstrapping and dependency pinning.
- Docker healthcheck stability and container readiness sequencing.
- Validation error serialization issues addressed with `jsonable_encoder`.
- Balancing production safety (no auto migrations in prod) with dev ergonomics.

### Manual interventions noted

- Optional Docker smoke tests require `RUN_DOCKER_TESTS=1` and Docker/Compose.
- Production migrations are manual on Render (documented in `README.md`).

## Root documentation inventory (explicit references)

- `README.md`: setup, environment, tests, Docker usage, Render deployment.
- `API.md`: endpoint references and auth usage.
- `SECURITY.md`: secrets, auth, audit logging notes.
- `ARCHITECTURE.md`: system architecture and operational concerns.
- `TECHNICAL_SPEC.md`: requirements, testing strategy, coverage target.
- `IMPLEMENTATION_PLAN.md`: phased TDD checkpoints and ordering.
- `MILESTONES.md`: completion status by phase.
- `ROADMAP.md`: future improvements and operational follow-ups.
- `DEPENDENCIES.md`: dependency rationale.
- `WORKFLOW.md`: git workflow and CI expectations.
- `CONTRIBUTING.md`: contributor workflow and TDD expectations.
- `AI_LOG.md`: AI usage and process logs per phase.
- `FDE_Tech_Assessment_(T2).md`: assessment requirements (unchanged).
- `requirements.txt`: pinned runtime dependencies.
- `requirements-dev.txt`: pinned dev/test dependencies.

## Scope and sources reviewed

Primary references for requirements and design:
- `FDE_Tech_Assessment_(T2).md`
- `TECHNICAL_SPEC.md`
- `ARCHITECTURE.md`
- `IMPLEMENTATION_PLAN.md`
- `MILESTONES.md`
- `ROADMAP.md`

Operational and usage documentation:
- `README.md`
- `API.md`
- `SECURITY.md`
- `DEPENDENCIES.md`
- `WORKFLOW.md`
- `CONTRIBUTING.md`
- `AI_LOG.md`
- `requirements.txt`
- `requirements-dev.txt`

AI interaction archives (prompts and iterations):
- `ai_chats/Banking service technical specification and rules.txt`
- `ai_chats/FDE tech assessment instructions.txt`
- `ai_chats/Phase 1: Project scaffolding and developer experience.txt`
- `ai_chats/Phase 2 production readiness foundations.txt`
- `ai_chats/Phase 3 core domain capabilities.txt`
- `ai_chats/Phase 4 correctness and safety guarantees.txt`
- `ai_chats/Phase 5 operational deliverables.txt`
- `ai_chats/Phase 5 bonus demo deliverables.txt`
- `ai_chats/Proper git workflow.txt`
- `ai_chats/System functionality and API questions.txt`
- `ai_chats/Test client and frontend implementation.txt`
- `ai_chats/Github to Render deployment.txt`

Agent transcripts (detailed step-by-step execution logs):
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/a993db9e-1b52-47f6-9a12-af572532e03c.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/9c730108-d8b5-4706-b603-6e6b8f0cd59e.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/fe48f89b-9795-4320-9ef0-7ed23c3f8855.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/c566e373-888b-4603-9055-573092092ea8.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/448dc459-2a51-4ac1-8ee1-d9d74ce4f1d7.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/42bcdd5e-795c-4d72-98fb-54c226b1af90.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/e192595f-e709-4b63-8635-621a4dfbf5fe.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/5135227d-8946-42b6-ba76-56b2c9ea1b98.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/453cea4f-8fb1-4b22-b9b6-07d9bbf67682.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/692af366-9d6b-48e5-af54-6c255ef0b149.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/37c1de31-82d0-4b82-b919-3b9c4dc94cf2.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/b0e4919b-79d0-49a9-a9b4-c6f4fc90ea35.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/438183e2-d291-4198-8957-5174be731faa.txt`
- `/home/mini/.cursor/projects/home-mini-Documents-coding-invisible-interview-cursor-banking-service/agent-transcripts/5508e9c7-e06e-4482-8bdd-b45c2d33c356.txt`
