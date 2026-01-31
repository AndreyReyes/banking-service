const state = {
  baseUrl: window.location.origin,
  users: [],
  activeUserKey: null,
  accountsByUser: {},
  expiryIntervalId: null,
  promptTimeoutId: null,
};

const logEl = document.getElementById("log");
const authStatusEl = document.getElementById("auth-status");
const accountsListEl = document.getElementById("accounts-list");
const statementOutputEl = document.getElementById("statement-output");
const tokenExpiryRelativeEl = document.getElementById("token-expiry-relative");
const tokenExpiryAbsoluteEl = document.getElementById("token-expiry-absolute");
const tokenRefreshPresentEl = document.getElementById("token-refresh-present");
const tokenLastRefreshEl = document.getElementById("token-last-refresh");
const keepAliveModal = document.getElementById("keep-alive-modal");
const keepAliveYes = document.getElementById("keep-alive-yes");
const keepAliveNo = document.getElementById("keep-alive-no");

const baseUrlInput = document.getElementById("base-url");
baseUrlInput.value = state.baseUrl;
baseUrlInput.addEventListener("input", () => {
  state.baseUrl = baseUrlInput.value.replace(/\/+$/, "");
});

function log(message, payload) {
  const line = payload ? `${message} ${JSON.stringify(payload, null, 2)}` : message;
  logEl.textContent = `${line}\n${logEl.textContent}`;
}

function getActiveUser() {
  return state.users.find((user) => user.key === state.activeUserKey) || null;
}

function getSelectedUserKey(form) {
  const select = form.querySelector("[data-user-select]");
  return select ? select.value : state.activeUserKey;
}

function formatTimestamp(value) {
  if (!value) {
    return "--";
  }
  const date = new Date(value);
  return `${date.toLocaleString()} (${date.toISOString()})`;
}

function formatRemaining(ms) {
  if (ms == null) {
    return "--";
  }
  if (ms <= 0) {
    return "Expired";
  }
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}m ${seconds.toString().padStart(2, "0")}s`;
}

function updateAuthStatus() {
  if (!state.activeUserKey) {
    authStatusEl.textContent = "Not authenticated";
    return;
  }
  const user = getActiveUser();
  authStatusEl.textContent = user
    ? `Active user: ${user.email} (${state.users.length} users)`
    : "Not authenticated";
}

function renderUserSelectors() {
  const selectors = document.querySelectorAll("[data-user-select]");
  selectors.forEach((select) => {
    const options = state.users.map(
      (user) => `<option value="${user.key}">${user.email}</option>`
    );
    if (!options.length) {
      select.innerHTML = `<option value="">No users logged in</option>`;
    } else {
      select.innerHTML = options.join("");
    }
    select.value = state.activeUserKey || "";
    if (!select.dataset.bound) {
      select.addEventListener("change", () => {
        setActiveUser(select.value);
      });
      select.dataset.bound = "true";
    }
  });
}

function renderAccounts() {
  const user = getActiveUser();
  const accounts = user ? state.accountsByUser[user.key] || [] : [];
  accountsListEl.innerHTML = accounts
    .map((account) => `<div>Account ${account.id} (${account.type})</div>`)
    .join("");
  [
    "deposit-account",
    "withdrawal-account",
    "transfer-from",
    "transfer-to",
    "statement-account",
  ].forEach((selectId) => {
    const select = document.getElementById(selectId);
    select.innerHTML = accounts
      .map(
        (account) =>
          `<option value="${account.id}">${account.id} (${account.type})</option>`
      )
      .join("");
  });
}

function updateTokenStatus() {
  const user = getActiveUser();
  if (!user) {
    tokenExpiryRelativeEl.textContent = "--";
    tokenExpiryAbsoluteEl.textContent = "--";
    tokenRefreshPresentEl.textContent = "--";
    tokenLastRefreshEl.textContent = "--";
    return;
  }
  const remainingMs = user.expiresAt ? user.expiresAt - Date.now() : null;
  tokenExpiryRelativeEl.textContent = formatRemaining(remainingMs);
  tokenExpiryAbsoluteEl.textContent = formatTimestamp(user.expiresAt);
  tokenRefreshPresentEl.textContent = user.refreshToken ? "Stored in memory" : "Missing";
  tokenLastRefreshEl.textContent = formatTimestamp(user.lastRefreshAt);
}

function scheduleExpiryPrompt() {
  if (state.promptTimeoutId) {
    clearTimeout(state.promptTimeoutId);
    state.promptTimeoutId = null;
  }
  const user = getActiveUser();
  if (!user || !user.expiresAt) {
    return;
  }
  const msUntilPrompt = user.expiresAt - Date.now() - 3 * 60 * 1000;
  if (msUntilPrompt <= 0) {
    return;
  }
  state.promptTimeoutId = setTimeout(() => {
    openKeepAlivePrompt();
  }, msUntilPrompt);
}

function startExpiryTicker() {
  if (state.expiryIntervalId) {
    clearInterval(state.expiryIntervalId);
  }
  state.expiryIntervalId = setInterval(() => {
    updateTokenStatus();
  }, 1000);
}

function openKeepAlivePrompt() {
  keepAliveModal.setAttribute("aria-hidden", "false");
  keepAliveModal.classList.add("is-open");
}

function closeKeepAlivePrompt() {
  keepAliveModal.setAttribute("aria-hidden", "true");
  keepAliveModal.classList.remove("is-open");
}

async function apiRequest(method, path, body, user, extraHeaders = {}) {
  const headers = { "Content-Type": "application/json", ...extraHeaders };
  if (user && user.accessToken) {
    headers.Authorization = `Bearer ${user.accessToken}`;
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

function setActiveUser(userKey) {
  state.activeUserKey = userKey || null;
  renderUserSelectors();
  updateAuthStatus();
  renderAccounts();
  updateTokenStatus();
  scheduleExpiryPrompt();
}

function upsertUser({ email, accessToken, refreshToken, expiresIn, deviceId }) {
  const key = email.toLowerCase();
  const expiresAt = Date.now() + expiresIn * 1000;
  const existing = state.users.find((user) => user.key === key);
  if (existing) {
    existing.accessToken = accessToken;
    existing.refreshToken = refreshToken;
    existing.expiresAt = expiresAt;
    existing.deviceId = deviceId;
    existing.lastRefreshAt = new Date().toISOString();
  } else {
    state.users.push({
      key,
      email,
      accessToken,
      refreshToken,
      expiresAt,
      deviceId,
      lastRefreshAt: null,
    });
    state.accountsByUser[key] = state.accountsByUser[key] || [];
  }
  setActiveUser(key);
}

async function refreshActiveUserToken() {
  const user = getActiveUser();
  if (!user) {
    log("Select a user before refreshing.");
    return;
  }
  if (!user.refreshToken) {
    log("No refresh token available; please log in again.");
    return;
  }
  const payload = await apiRequest(
    "POST",
    "/v1/auth/refresh",
    { refresh_token: user.refreshToken },
    null,
    { "X-Device-Id": user.deviceId || "demo-web" }
  );
  upsertUser({
    email: user.email,
    accessToken: payload.access_token,
    refreshToken: payload.refresh_token,
    expiresIn: payload.expires_in,
    deviceId: user.deviceId,
  });
  log("Token refreshed.");
}

document.getElementById("refresh-token").addEventListener("click", async () => {
  try {
    await refreshActiveUserToken();
  } catch (error) {
    log(error.message);
  }
});

keepAliveYes.addEventListener("click", async () => {
  closeKeepAlivePrompt();
  try {
    await refreshActiveUserToken();
  } catch (error) {
    log(error.message);
  }
});

keepAliveNo.addEventListener("click", () => {
  closeKeepAlivePrompt();
  log("Session refresh dismissed; token will expire.");
});

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
      null,
      { "X-Device-Id": formData.device_id || "demo-web" }
    );
    upsertUser({
      email: formData.email,
      accessToken: payload.access_token,
      refreshToken: payload.refresh_token,
      expiresIn: payload.expires_in,
      deviceId: formData.device_id || "demo-web",
    });
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
  const userKey = getSelectedUserKey(form);
  const user = state.users.find((entry) => entry.key === userKey);
  if (!user) {
    log("Select a user before creating an account.");
    return;
  }
  try {
    const payload = await apiRequest("POST", "/v1/accounts", formData, user);
    state.accountsByUser[user.key].push(payload);
    renderAccounts();
    log(`Account created for ${user.email}.`, payload);
  } catch (error) {
    log(error.message);
  }
});

document.getElementById("deposit-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const formData = Object.fromEntries(new FormData(form).entries());
  const userKey = getSelectedUserKey(form);
  const user = state.users.find((entry) => entry.key === userKey);
  if (!user) {
    log("Select a user before depositing.");
    return;
  }
  try {
    await apiRequest(
      "POST",
      "/v1/transactions",
      {
        account_id: Number(document.getElementById("deposit-account").value),
        type: "deposit",
        amount: Number(formData.amount),
        currency: formData.currency,
      },
      user
    );
    log(`Deposit created for ${user.email}.`);
  } catch (error) {
    log(error.message);
  }
});

document.getElementById("withdrawal-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const formData = Object.fromEntries(new FormData(form).entries());
  const userKey = getSelectedUserKey(form);
  const user = state.users.find((entry) => entry.key === userKey);
  if (!user) {
    log("Select a user before withdrawing.");
    return;
  }
  try {
    await apiRequest(
      "POST",
      "/v1/transactions",
      {
        account_id: Number(document.getElementById("withdrawal-account").value),
        type: "withdrawal",
        amount: Number(formData.amount),
        currency: formData.currency,
      },
      user
    );
    log(`Withdrawal created for ${user.email}.`);
  } catch (error) {
    log(error.message);
  }
});

document.getElementById("transfer-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const formData = Object.fromEntries(new FormData(form).entries());
  const userKey = getSelectedUserKey(form);
  const user = state.users.find((entry) => entry.key === userKey);
  if (!user) {
    log("Select a user before transferring.");
    return;
  }
  try {
    await apiRequest(
      "POST",
      "/v1/transfers",
      {
        from_account_id: Number(document.getElementById("transfer-from").value),
        to_account_id: Number(document.getElementById("transfer-to").value),
        amount: Number(formData.amount),
        currency: formData.currency,
      },
      user
    );
    log(`Transfer created for ${user.email}.`);
  } catch (error) {
    log(error.message);
  }
});

document.getElementById("statement-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const userKey = getSelectedUserKey(form);
  const user = state.users.find((entry) => entry.key === userKey);
  if (!user) {
    log("Select a user before fetching a statement.");
    return;
  }
  try {
    const accountId = Number(document.getElementById("statement-account").value);
    const payload = await apiRequest("GET", `/v1/statements/${accountId}`, null, user);
    statementOutputEl.textContent = JSON.stringify(payload, null, 2);
    log(`Statement fetched for ${user.email}.`);
  } catch (error) {
    log(error.message);
  }
});

renderUserSelectors();
updateAuthStatus();
updateTokenStatus();
startExpiryTicker();
