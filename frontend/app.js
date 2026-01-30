const state = {
  baseUrl: "http://localhost:8000",
  token: null,
  accounts: [],
};

const logEl = document.getElementById("log");
const authStatusEl = document.getElementById("auth-status");
const accountsListEl = document.getElementById("accounts-list");
const statementOutputEl = document.getElementById("statement-output");

const baseUrlInput = document.getElementById("base-url");
baseUrlInput.addEventListener("input", () => {
  state.baseUrl = baseUrlInput.value.replace(/\/+$/, "");
});

function log(message, payload) {
  const line = payload ? `${message} ${JSON.stringify(payload, null, 2)}` : message;
  logEl.textContent = `${line}\n${logEl.textContent}`;
}

function updateAuthStatus() {
  authStatusEl.textContent = state.token ? "Authenticated" : "Not authenticated";
}

function renderAccounts() {
  accountsListEl.innerHTML = state.accounts
    .map((account) => `<div>Account ${account.id} (${account.type})</div>`)
    .join("");
  ["deposit-account", "transfer-from", "transfer-to", "statement-account"].forEach(
    (selectId) => {
      const select = document.getElementById(selectId);
      select.innerHTML = state.accounts
        .map(
          (account) =>
            `<option value="${account.id}">${account.id} (${account.type})</option>`
        )
        .join("");
    }
  );
}

async function apiRequest(method, path, body, extraHeaders = {}) {
  const headers = { "Content-Type": "application/json", ...extraHeaders };
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }
  const response = await fetch(`${state.baseUrl}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await response.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }
  if (!response.ok) {
    throw new Error(`${method} ${path} failed (${response.status}): ${text}`);
  }
  return payload;
}

document.getElementById("signup-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    await apiRequest("POST", "/v1/auth/signup", payload);
    log("Signup successful.");
    form.reset();
  } catch (error) {
    log(error.message);
  }
});

document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const formData = Object.fromEntries(new FormData(form).entries());
  try {
    const payload = await apiRequest(
      "POST",
      "/v1/auth/login",
      {
        email: formData.email,
        password: formData.password,
      },
      { "X-Device-Id": formData.device_id || "demo-web" }
    );
    state.token = payload.access_token;
    updateAuthStatus();
    log("Login successful.");
  } catch (error) {
    log(error.message);
  }
});

document.getElementById("account-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const formData = Object.fromEntries(new FormData(form).entries());
  try {
    const payload = await apiRequest("POST", "/v1/accounts", formData);
    state.accounts.push(payload);
    renderAccounts();
    log("Account created.", payload);
  } catch (error) {
    log(error.message);
  }
});

document.getElementById("deposit-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const formData = Object.fromEntries(new FormData(form).entries());
  try {
    await apiRequest("POST", "/v1/transactions", {
      account_id: Number(document.getElementById("deposit-account").value),
      type: "deposit",
      amount: Number(formData.amount),
      currency: formData.currency,
    });
    log("Deposit created.");
  } catch (error) {
    log(error.message);
  }
});

document.getElementById("transfer-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const formData = Object.fromEntries(new FormData(form).entries());
  try {
    await apiRequest("POST", "/v1/transfers", {
      from_account_id: Number(document.getElementById("transfer-from").value),
      to_account_id: Number(document.getElementById("transfer-to").value),
      amount: Number(formData.amount),
      currency: formData.currency,
    });
    log("Transfer created.");
  } catch (error) {
    log(error.message);
  }
});

document.getElementById("statement-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const accountId = Number(document.getElementById("statement-account").value);
    const payload = await apiRequest("GET", `/v1/statements/${accountId}`);
    statementOutputEl.textContent = JSON.stringify(payload, null, 2);
    log("Statement fetched.");
  } catch (error) {
    log(error.message);
  }
});

updateAuthStatus();
