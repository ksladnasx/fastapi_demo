const storageKey = "fastapi_demo_access_token";

let jobsPage = 1;
let jobsTotal = 0;

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
  resultLog: document.querySelector("#resultLog"),
  registerBtn: document.querySelector("#registerBtn"),
  loginBtn: document.querySelector("#loginBtn"),
  saveTokenBtn: document.querySelector("#saveTokenBtn"),
  clearTokenBtn: document.querySelector("#clearTokenBtn"),
  meBtn: document.querySelector("#meBtn"),
  usersBtn: document.querySelector("#usersBtn"),
  clearLogBtn: document.querySelector("#clearLogBtn"),
  jobKeyword: document.querySelector("#jobKeyword"),
  jobLocation: document.querySelector("#jobLocation"),
  jobStatus: document.querySelector("#jobStatus"),
  jobPageSize: document.querySelector("#jobPageSize"),
  importPages: document.querySelector("#importPages"),
  importStartPage: document.querySelector("#importStartPage"),
  importJobsBtn: document.querySelector("#importJobsBtn"),
  loadJobsBtn: document.querySelector("#loadJobsBtn"),
  prevJobsBtn: document.querySelector("#prevJobsBtn"),
  nextJobsBtn: document.querySelector("#nextJobsBtn"),
  jobsList: document.querySelector("#jobsList"),
  jobMeta: document.querySelector("#jobMeta"),
};

nodes.tokenBox.value = localStorage.getItem(storageKey) || "";
renderAuthHeader();

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
  const body = {
    username: nodes.loginUsername.value.trim(),
    password: nodes.loginPassword.value,
  };

  const response = await sendRequest("POST", "/user/login", { body });
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

nodes.clearLogBtn.addEventListener("click", () => {
  nodes.resultLog.textContent = "等待操作...";
});

nodes.tokenBox.addEventListener("input", renderAuthHeader);

nodes.loadJobsBtn.addEventListener("click", async () => {
  jobsPage = 1;
  await loadJobs();
});

nodes.prevJobsBtn.addEventListener("click", async () => {
  if (jobsPage > 1) {
    jobsPage -= 1;
    await loadJobs();
  }
});

nodes.nextJobsBtn.addEventListener("click", async () => {
  const pageSize = getJobPageSize();
  if (jobsPage * pageSize < jobsTotal) {
    jobsPage += 1;
    await loadJobs();
  }
});

nodes.importJobsBtn.addEventListener("click", async () => {
  const pages = Math.max(1, Number(nodes.importPages.value || 30));
  const startPage = Math.max(1, Number(nodes.importStartPage.value || 1));
  const path = `/recruitment/import/givemeoc?pages=${pages}&start_page=${startPage}`;
  nodes.importJobsBtn.disabled = true;
  nodes.importJobsBtn.textContent = "导入中...";
  try {
    const response = await sendRequest("POST", path, { auth: true });
    if (response?.code === 0) {
      await loadJobs();
    }
  } finally {
    nodes.importJobsBtn.disabled = false;
    nodes.importJobsBtn.textContent = "爬取并入库";
  }
});

async function loadJobs() {
  const params = new URLSearchParams({
    page: String(jobsPage),
    page_size: String(getJobPageSize()),
  });
  appendOptionalParam(params, "keyword", nodes.jobKeyword.value.trim());
  appendOptionalParam(params, "location", nodes.jobLocation.value.trim());
  appendOptionalParam(params, "progress_status", nodes.jobStatus.value.trim());

  const response = await sendRequest("GET", `/recruitment/jobs?${params.toString()}`);
  if (response?.data) {
    jobsTotal = response.data.total || 0;
    renderJobs(response.data);
  }
}

function renderJobs(data) {
  const jobs = data.items || [];
  nodes.jobMeta.textContent = `共 ${data.total} 条，第 ${data.page} 页`;

  if (!jobs.length) {
    nodes.jobsList.innerHTML = `<div class="empty-state">没有找到招聘信息。</div>`;
    return;
  }

  nodes.jobsList.innerHTML = jobs
    .map((job) => {
      const title = escapeHtml(job.job_title || "未命名职位");
      const company = escapeHtml(job.company_name || "未知公司");
      const location = escapeHtml(job.location || "地点未标注");
      const status = escapeHtml(job.progress_status || "状态未标注");
      const deadline = escapeHtml(job.deadline || "截止日期未标注");
      const summary = escapeHtml(job.summary || "");
      const officialUrl = renderLink(job.official_url, "官网");
      const recruitmentUrl = renderLink(job.recruitment_url, "招聘链接");

      return `
        <article class="job-row">
          <div>
            <h3>${title}</h3>
            <p>${company}</p>
          </div>
          <div class="job-tags">
            <span>${location}</span>
            <span>${status}</span>
            <span>${deadline}</span>
          </div>
          <p class="job-summary">${summary}</p>
          <div class="job-links">
            ${officialUrl}
            ${recruitmentUrl}
          </div>
        </article>
      `;
    })
    .join("");
}

async function sendRequest(method, path, options = {}) {
  const url = `${getBaseUrl()}${path}`;
  const headers = {
    "Content-Type": "application/json",
  };

  if (options.auth) {
    headers.Authorization = `Bearer ${getToken()}`;
  }

  renderAuthHeader(headers.Authorization);
  writeLog(
    formatBlock("Request", {
      method,
      url,
      headers,
      body: options.body || null,
    }),
    { append: false },
  );

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    const data = await readJson(response);

    writeLog(
      formatBlock("Response", {
        status: response.status,
        ok: response.ok,
        data,
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

function appendOptionalParam(params, key, value) {
  if (value) {
    params.set(key, value);
  }
}

function getBaseUrl() {
  return nodes.apiBaseUrl.value.trim().replace(/\/$/, "");
}

function getToken() {
  return nodes.tokenBox.value.trim();
}

function getJobPageSize() {
  return Math.min(100, Math.max(1, Number(nodes.jobPageSize.value || 20)));
}

function renderAuthHeader(value) {
  const header = value || (getToken() ? `Bearer ${getToken()}` : "Bearer 未设置");
  nodes.authHeader.textContent = `Authorization: ${header}`;
}

function renderLink(url, label) {
  if (!url) {
    return "";
  }
  return `<a href="${escapeAttribute(url)}" target="_blank" rel="noreferrer">${label}</a>`;
}

function writeLog(content, { append }) {
  if (append) {
    nodes.resultLog.textContent += `\n\n${content}`;
  } else {
    nodes.resultLog.textContent = content;
  }
}

function formatBlock(title, value) {
  return `${title}\n${JSON.stringify(value, null, 2)}`;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/`/g, "&#096;");
}
