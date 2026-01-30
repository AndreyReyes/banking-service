#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


@dataclass
class DemoContext:
    base_url: str
    access_token: str | None = None
    saved: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.saved is None:
            self.saved = {}


def _normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def _request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> tuple[int, Any | None]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if extra_headers:
        for key, value in extra_headers.items():
            req.add_header(key, value)
    try:
        with request.urlopen(req) as response:
            body = response.read()
            return response.status, json.loads(body) if body else None
    except error.HTTPError as exc:
        body = exc.read()
        parsed = None
        if body:
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = body.decode("utf-8", errors="ignore")
        return exc.code, parsed


def _expect(status_code: int, expected: int, payload: Any, label: str) -> Any:
    if status_code != expected:
        raise RuntimeError(f"{label} failed ({status_code}): {payload}")
    return payload


def _print_step(message: str) -> None:
    print(f"-> {message}")


def _prompt(label: str, default: str) -> str:
    raw = input(f"{label} [{default}]: ").strip()
    return raw or default


def _prompt_int(label: str, default: int) -> int:
    raw = input(f"{label} [{default}]: ").strip()
    return int(raw) if raw else default


def _signup(context: DemoContext, payload: dict[str, Any]) -> None:
    status, body = _request_json(
        "POST", f"{context.base_url}/v1/auth/signup", payload=payload
    )
    _expect(status, 201, body, "Signup")


def _login(context: DemoContext, email: str, password: str, device_id: str) -> None:
    status, body = _request_json(
        "POST",
        f"{context.base_url}/v1/auth/login",
        payload={"email": email, "password": password},
        extra_headers={"X-Device-Id": device_id},
    )
    payload = _expect(status, 200, body, "Login")
    context.access_token = payload["access_token"]
    context.saved["tokens"] = payload


def _create_account(context: DemoContext, account_type: str, currency: str) -> int:
    status, body = _request_json(
        "POST",
        f"{context.base_url}/v1/accounts",
        payload={"type": account_type, "currency": currency},
        token=context.access_token,
    )
    payload = _expect(status, 201, body, "Create account")
    return payload["id"]


def _deposit(context: DemoContext, account_id: int, amount: int, currency: str) -> None:
    status, body = _request_json(
        "POST",
        f"{context.base_url}/v1/transactions",
        payload={
            "account_id": account_id,
            "type": "deposit",
            "amount": amount,
            "currency": currency,
        },
        token=context.access_token,
    )
    _expect(status, 201, body, "Deposit")


def _transfer(
    context: DemoContext, from_id: int, to_id: int, amount: int, currency: str
) -> None:
    status, body = _request_json(
        "POST",
        f"{context.base_url}/v1/transfers",
        payload={
            "from_account_id": from_id,
            "to_account_id": to_id,
            "amount": amount,
            "currency": currency,
        },
        token=context.access_token,
    )
    _expect(status, 201, body, "Transfer")


def _statement(context: DemoContext, account_id: int) -> dict[str, Any]:
    status, body = _request_json(
        "GET",
        f"{context.base_url}/v1/statements/{account_id}",
        token=context.access_token,
    )
    return _expect(status, 200, body, "Statement")


def run_interactive(base_url: str) -> None:
    context = DemoContext(base_url=_normalize_base_url(base_url))
    print("Banking demo client (interactive)")
    print("Amounts are in minor units (cents).")

    email = _prompt("Email", "demo@example.com")
    password = _prompt("Password", "supersecure123")
    first_name = _prompt("First name", "Ada")
    last_name = _prompt("Last name", "Lovelace")
    dob = _prompt("Date of birth (YYYY-MM-DD)", "1990-01-01")
    currency = _prompt("Currency", "USD")
    device_id = _prompt("Device ID", "demo-cli")

    _print_step("Signing up")
    _signup(
        context,
        {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
        },
    )

    _print_step("Logging in")
    _login(context, email, password, device_id)

    source_type = _prompt("Source account type", "checking")
    dest_type = _prompt("Destination account type", "savings")

    _print_step("Creating source account")
    source_account_id = _create_account(context, source_type, currency)
    _print_step(f"Source account ID: {source_account_id}")

    _print_step("Creating destination account")
    destination_account_id = _create_account(context, dest_type, currency)
    _print_step(f"Destination account ID: {destination_account_id}")

    deposit_amount = _prompt_int("Deposit amount", 10000)
    transfer_amount = _prompt_int("Transfer amount", 2500)

    _print_step("Depositing funds")
    _deposit(context, source_account_id, deposit_amount, currency)

    _print_step("Transferring funds")
    _transfer(context, source_account_id, destination_account_id, transfer_amount, currency)

    _print_step("Fetching statements")
    source_statement = _statement(context, source_account_id)
    destination_statement = _statement(context, destination_account_id)

    print("Source statement balance:", source_statement["balance"])
    print("Destination statement balance:", destination_statement["balance"])
    print("Demo flow completed successfully.")


def _resolve_ref(context: DemoContext, value: Any, label: str) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value in context.saved:
        return int(context.saved[value])
    raise ValueError(f"Unknown {label} reference: {value}")


def run_config(base_url: str | None, config_path: str) -> None:
    raw = json.loads(Path(config_path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Config must be a JSON object.")
    config_base_url = raw.get("base_url")
    resolved_base_url = base_url or config_base_url or "http://localhost:8000"
    context = DemoContext(base_url=_normalize_base_url(resolved_base_url))
    steps = raw.get("steps", [])
    if not isinstance(steps, list):
        raise ValueError("Config 'steps' must be a list.")

    for step in steps:
        action = step.get("action")
        _print_step(f"Running {action}")
        if action == "signup":
            _signup(
                context,
                {
                    "email": step["email"],
                    "password": step["password"],
                    "first_name": step.get("first_name", "Ada"),
                    "last_name": step.get("last_name", "Lovelace"),
                    "dob": step.get("dob", "1990-01-01"),
                },
            )
        elif action == "login":
            _login(
                context,
                step["email"],
                step["password"],
                step.get("device_id", "demo-cli"),
            )
        elif action == "create_account":
            account_id = _create_account(
                context, step.get("type", "checking"), step.get("currency", "USD")
            )
            if step.get("save_as"):
                context.saved[step["save_as"]] = account_id
        elif action == "deposit":
            account_id = _resolve_ref(
                context,
                step.get("account_id") or step["account_ref"],
                "account",
            )
            _deposit(
                context,
                account_id,
                int(step["amount"]),
                step.get("currency", "USD"),
            )
        elif action == "transfer":
            from_id = _resolve_ref(
                context,
                step.get("from_account_id") or step["from_account_ref"],
                "from_account",
            )
            to_id = _resolve_ref(
                context,
                step.get("to_account_id") or step["to_account_ref"],
                "to_account",
            )
            _transfer(
                context,
                from_id,
                to_id,
                int(step["amount"]),
                step.get("currency", "USD"),
            )
        elif action == "statement":
            account_id = _resolve_ref(
                context, step.get("account_id") or step["account_ref"], "account"
            )
            statement = _statement(context, account_id)
            if step.get("save_as"):
                context.saved[step["save_as"]] = statement
        else:
            raise ValueError(f"Unknown action: {action}")

    print("Config demo flow completed successfully.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Banking service demo client")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--interactive", action="store_true", help="Run interactive demo flow")
    group.add_argument("--config", help="Run config-driven demo flow")
    parser.add_argument("--base-url", help="Override base URL (e.g. http://localhost:8000)")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])
    if args.interactive:
        run_interactive(args.base_url or "http://localhost:8000")
    else:
        run_config(args.base_url, args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
