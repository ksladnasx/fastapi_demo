const storageKey = "fastapi_demo_access_token";

const nodes = {
  apiBaseUrl: document.querySelector("#apiBaseUrl"),
  registerUsername: document.querySelector("#registerUsername"),
  registerEmail: document.querySelector("#registerEmail"),
  registerFullName: document.querySelector("#registerFullName"),
  registerPassword: document.querySelector("#registerPassword"),
  loginUsername: document.querySelector("#loginUsername"),
  loginPassword: document.querySelector("#loginPassword"),
  tokenBox: document.querySelector("#tokenBox"),
  authHeader: document.querySelector("#authHeader"),
  documentCookie: document.querySelector("#documentCookie"),
  resultLog: document.querySelector("#resultLog"),
  registerBtn: document.querySelector("#registerBtn"),
  loginBtn: document.querySelector("#loginBtn"),
  saveTokenBtn: document.querySelector("#saveTokenBtn"),
  clearTokenBtn: document.querySelector("#clearTokenBtn"),
  meBtn: document.querySelector("#meBtn"),
  usersBtn: document.querySelector("#usersBtn"),
  cookieLoginBtn: document.querySelector("#cookieLoginBtn"),
  cookieMeBtn: document.querySelector("#cookieMeBtn"),
  cookieLogoutBtn: document.querySelector("#cookieLogoutBtn"),
  visibleCookieBtn: document.querySelector("#visibleCookieBtn"),
  clearVisibleCookieBtn: document.querySelector("#clearVisibleCookieBtn"),
  refreshDocumentCookieBtn: document.querySelector("#refreshDocumentCookieBtn"),
  clearLogBtn: document.querySelector("#clearLogBtn"),
};

nodes.tokenBox.value = localStorage.getItem(storageKey) || "";
renderAuthHeader();
renderDocumentCookie();

nodes.registerBtn.addEventListener("click", async () => {
  const body = {
    username: nodes.registerUsername.value.trim(),
    email: nodes.registerEmail.value.trim(),
    full_name: nodes.registerFullName.value.trim() || null,
    password: nodes.registerPassword.value,
    is_active: true,
  };

  await sendRequest("POST", "/user/register", { body });
});

nodes.loginBtn.addEventListener("click", async () => {
  const response = await sendRequest("POST", "/user/login", { body: getLoginBody() });
  const token = response?.data?.access_token;
  if (token) {
    nodes.tokenBox.value = token;
    localStorage.setItem(storageKey, token);
    renderAuthHeader();
  }
});

nodes.saveTokenBtn.addEventListener("click", () => {
  localStorage.setItem(storageKey, getToken());
  renderAuthHeader();
  writeLog("Token 已保存到 localStorage。", { append: false });
});

nodes.clearTokenBtn.addEventListener("click", () => {
  nodes.tokenBox.value = "";
  localStorage.removeItem(storageKey);
  renderAuthHeader();
  writeLog("Token 已清空。", { append: false });
});

nodes.meBtn.addEventListener("click", async () => {
  await sendRequest("GET", "/user/me", { auth: true });
});

nodes.usersBtn.addEventListener("click", async () => {
  await sendRequest("GET", "/user/get_users?page=1&page_size=10", { auth: true });
});

nodes.cookieLoginBtn.addEventListener("click", async () => {
  await sendRequest("POST", "/cookie/login", { body: getLoginBody() });
  renderDocumentCookie();
});

nodes.cookieMeBtn.addEventListener("click", async () => {
  await sendRequest("GET", "/cookie/me");
  renderDocumentCookie();
});

nodes.cookieLogoutBtn.addEventListener("click", async () => {
  await sendRequest("POST", "/cookie/logout");
  renderDocumentCookie();
});

nodes.visibleCookieBtn.addEventListener("click", async () => {
  await sendRequest("POST", "/cookie/visible");
  renderDocumentCookie();
});

nodes.clearVisibleCookieBtn.addEventListener("click", async () => {
  await sendRequest("DELETE", "/cookie/visible");
  renderDocumentCookie();
});

nodes.refreshDocumentCookieBtn.addEventListener("click", renderDocumentCookie);

nodes.clearLogBtn.addEventListener("click", () => {
  nodes.resultLog.textContent = "等待操作...";
});

nodes.tokenBox.addEventListener("input", renderAuthHeader);

function getLoginBody() {
  return {
    username: nodes.loginUsername.value.trim(),
    password: nodes.loginPassword.value,
  };
}

async function sendRequest(method, path, options = {}) {
  const url = getBaseUrl() + path;
  const headers = {};

  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (options.auth) {
    headers.Authorization = "Bearer " + getToken();
  }

  renderAuthHeader(headers.Authorization);
  writeLog(
    formatBlock("Request", {
      method,
      url,
      credentials: "include",
      headers,
      body: options.body || null,
    }),
    { append: false },
  );

  try {
    const response = await fetch(url, {
      method,
      headers,
      credentials: "include",
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
    const data = await readJson(response);

    writeLog(
      formatBlock("Response", {
        status: response.status,
        ok: response.ok,
        data,
        note:
          path.startsWith("/cookie/")
            ? "如果接口设置了 Cookie，请在浏览器开发者工具的 Application / Cookies 中查看。JavaScript 不能读取 Set-Cookie 响应头。"
            : undefined,
      }),
      { append: true },
    );

    return data;
  } catch (error) {
    writeLog(
      formatBlock("Error", {
        message: error.message,
        hint: "请确认 FastAPI 服务已启动，并且 API 地址填写正确。",
      }),
      { append: true },
    );
    return null;
  }
}

async function readJson(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function getBaseUrl() {
  return nodes.apiBaseUrl.value.trim().replace(/\/$/, "");
}

function getToken() {
  return nodes.tokenBox.value.trim();
}

function renderAuthHeader(value) {
  const header = value || (getToken() ? "Bearer " + getToken() : "Bearer 未设置");
  nodes.authHeader.textContent = "Authorization: " + header;
}

function renderDocumentCookie() {
  nodes.documentCookie.textContent = "document.cookie: " + (document.cookie || "空");
}

function writeLog(text, { append } = { append: true }) {
  if (append) {
    nodes.resultLog.textContent += "\n\n" + text;
  } else {
    nodes.resultLog.textContent = text;
  }
}

function formatBlock(title, payload) {
  return title + "\n" + JSON.stringify(payload, null, 2);
}
