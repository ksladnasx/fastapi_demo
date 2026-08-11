from __future__ import annotations

import hashlib
import html
import json
import os
import re
import time
from html.parser import HTMLParser
from urllib.parse import urlencode, urljoin
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings

AJAX_URL = "https://www.givemeoc.com/wp-admin/admin-ajax.php"
BASE_URL = "https://www.givemeoc.com/"
LINK_KEYWORDS = (
    "career",
    "careers",
    "job",
    "jobs",
    "join",
    "recruit",
    "campus",
    "graduate",
    "intern",
    "greenhouse",
    "lever",
    "workday",
    "ashby",
    "smartrecruiters",
    "successfactors",
    "myworkdayjobs",
)
TITLE_KEYWORDS = (
    "engineer",
    "developer",
    "analyst",
    "designer",
    "manager",
    "intern",
    "graduate",
    "trainee",
    "职位",
    "岗位",
    "招聘",
    "实习",
    "校招",
    "全职",
)


class TextAndLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str] = []
        self._current_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        if tag == "a":
            self._current_href = attrs_map.get("href")
            if self._current_href:
                self.links.append(urljoin(BASE_URL, self._current_href))
        if tag in {"br", "p", "li", "tr", "td", "div", "span", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._current_href = None
        if tag in {"p", "li", "tr", "td", "div", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())

    @property
    def text(self) -> str:
        text = html.unescape(" ".join(self.parts))
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"\n\s*", "\n", text)
        return text.strip()


def crawl_givemeoc(
    *,
    start_page: int = 1,
    pages: int = 30,
    nonce: str | None = None,
    cookie: str | None = None,
    delay_seconds: float | None = None,
) -> list[dict]:
    nonce = nonce or settings.GIVEMEOC_NONCE
    cookie = cookie or settings.GIVEMEOC_COOKIE
    delay_seconds = (
        delay_seconds
        if delay_seconds is not None
        else settings.GIVEMEOC_REQUEST_DELAY_SECONDS
    )

    if not nonce:
        raise ValueError("Missing GIVEMEOC_NONCE in environment or .env")
    if not cookie:
        raise ValueError("Missing GIVEMEOC_COOKIE in environment or .env")

    all_jobs: list[dict] = []
    seen_keys: set[str] = set()

    for page in range(start_page, start_page + pages):
        html_text = fetch_givemeoc_page(page=page, nonce=nonce, cookie=cookie)
        for job in parse_givemeoc_html(html_text, source_page=page):
            if job["source_key"] not in seen_keys:
                seen_keys.add(job["source_key"])
                all_jobs.append(job)
        if delay_seconds > 0 and page < start_page + pages - 1:
            time.sleep(delay_seconds)

    return all_jobs


def fetch_givemeoc_page(*, page: int, nonce: str, cookie: str) -> str:
    body = urlencode(
        {
            "action": "filter_companies",
            "nonce": nonce,
            "paged": page,
            "company_name": "",
            "location": "",
            "target_candidates": "",
            "position": "",
            "progress_status": "",
            "deadline_range": "",
        }
    ).encode("utf-8")
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": cookie,
        "origin": BASE_URL.rstrip("/"),
        "priority": "u=1, i",
        "referer": BASE_URL,
        "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "x-requested-with": "XMLHttpRequest",
    }
    request = Request(AJAX_URL, data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=settings.GIVEMEOC_TIMEOUT_SECONDS) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            raw_text = _decode_response(response.read(), charset)
            return extract_html_payload(raw_text)
    except HTTPError as error:
        body_text = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(
            f"GivemeOC request failed on page {page}: HTTP {error.code} {error.reason}. "
            f"Response body: {body_text!r}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            f"GivemeOC request failed on page {page}: {error.reason}"
        ) from error


def parse_givemeoc_html(html_text: str, *, source_page: int) -> list[dict]:
    blocks = _extract_candidate_blocks(html_text)
    jobs: list[dict] = []

    for block in blocks:
        parsed = TextAndLinkParser()
        parsed.feed(block)
        text = parsed.text

        if 'class="crt-honeypot-row"' in block:
            continue

        links = _clean_links(parsed.links)
        if "<tr" in block and "data-id=" in block:
            job = _build_table_job(block=block, links=links, source_page=source_page)
        else:
            if len(text) < 10 or not links:
                continue
            job = _build_job(
                text=text,
                links=links,
                raw_html=block,
                source_page=source_page,
            )

        if not job["company_name"] and not job["job_title"]:
            continue
        jobs.append(job)

    return _dedupe_jobs(jobs)


def extract_html_payload(raw_text: str) -> str:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return raw_text

    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("html"), str):
            return data["html"]
        if isinstance(data, str):
            return data
        if isinstance(payload.get("html"), str):
            return payload["html"]

    return raw_text


def _decode_response(raw_bytes: bytes, charset: str) -> str:
    encodings = [charset, "utf-8", "gb18030"]
    for encoding in dict.fromkeys(encodings):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode(charset, errors="replace")


def _extract_candidate_blocks(html_text: str) -> list[str]:
    normalized = html_text.strip()
    candidates: list[str] = []

    data_row_pattern = re.compile(
        r"<tr\b(?=[^>]*data-id=)(?![^>]*crt-honeypot-row)[^>]*>.*?</tr>",
        re.IGNORECASE | re.DOTALL,
    )
    candidates.extend(match.group(0) for match in data_row_pattern.finditer(normalized))
    if candidates:
        return candidates

    class_pattern = re.compile(
        r"<(?P<tag>article|li|tr|div)\b(?=[^>]*(?:company|job|career|recruit|position|deadline|oc-))"
        r"[^>]*>.*?</(?P=tag)>",
        re.IGNORECASE | re.DOTALL,
    )
    candidates.extend(match.group(0) for match in class_pattern.finditer(normalized))

    if len(candidates) < 3:
        for tag in ("article", "tr", "li"):
            pattern = re.compile(
                rf"<{tag}\b[^>]*>.*?</{tag}>", re.IGNORECASE | re.DOTALL
            )
            candidates.extend(match.group(0) for match in pattern.finditer(normalized))

    if len(candidates) < 3 and normalized:
        candidates.append(normalized)

    useful_blocks = []
    seen_hashes = set()
    for candidate in candidates:
        if "href" not in candidate.lower():
            continue
        digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
        if digest not in seen_hashes:
            seen_hashes.add(digest)
            useful_blocks.append(candidate)

    return useful_blocks


def _build_table_job(*, block: str, links: list[str], source_page: int) -> dict:
    data_id = _extract_attr(block, "data-id")
    company_name = _extract_col(block, "crt-col-company")
    recruitment_type = _extract_col(block, "crt-col-recruitment-type")
    industry = _extract_col(block, "crt-col-industry")
    target_candidates = _extract_col(block, "crt-col-target")
    location = _extract_col(block, "crt-col-location")
    job_title = _extract_col(block, "crt-col-position")
    progress_status = _extract_attr(block, "data-original-status")
    progress_status = progress_status or _extract_col(block, "crt-col-status")
    update_time = _extract_col(block, "crt-col-update-time")
    deadline = _extract_col(block, "crt-col-deadline")
    company_size = _extract_col(block, "crt-col-company-size")
    notes = _extract_col(block, "crt-col-notes")
    official_url = _pick_official_url(links)
    recruitment_url = _pick_recruitment_url(links) or official_url
    identity = data_id or "|".join(
        part
        for part in (company_name, recruitment_type, target_candidates, deadline)
        if part
    )
    source_key = hashlib.sha256(f"givemeoc|{identity}".encode("utf-8")).hexdigest()
    summary_parts = [
        part
        for part in (
            company_name,
            industry,
            recruitment_type,
            target_candidates,
            location,
            job_title,
            progress_status,
            update_time,
            deadline,
            company_size,
            notes,
        )
        if part
    ]

    return {
        "source_site": "givemeoc",
        "source_page": source_page,
        "source_key": source_key,
        "company_name": _truncate(company_name, 255),
        "job_title": _truncate(job_title, 255),
        "location": _truncate(location, 255),
        "target_candidates": _truncate(target_candidates, 255),
        "position": _truncate(recruitment_type, 255),
        "progress_status": _truncate(progress_status, 255),
        "deadline": _truncate(deadline, 255),
        "official_url": _truncate(official_url, 1024),
        "recruitment_url": _truncate(recruitment_url, 1024),
        "summary": _truncate(" | ".join(summary_parts), 2000),
        "raw_html": _truncate(block, 65000),
    }


def _build_job(
    *,
    text: str,
    links: list[str],
    raw_html: str,
    source_page: int,
) -> dict:
    lines = _text_lines(text)
    company_name = _extract_labeled_value(text, ("公司", "Company")) or _guess_company(lines)
    job_title = _extract_labeled_value(text, ("职位", "岗位", "Position", "Role"))
    job_title = job_title or _guess_title(lines)
    location = _extract_labeled_value(text, ("地点", "地区", "Location"))
    target_candidates = _extract_labeled_value(text, ("对象", "Target Candidates"))
    position = _extract_labeled_value(text, ("类别", "类型", "Position Type"))
    progress_status = _extract_labeled_value(text, ("进度", "状态", "Status"))
    deadline = _extract_labeled_value(text, ("截止", "Deadline"))
    official_url = _pick_official_url(links)
    recruitment_url = _pick_recruitment_url(links) or official_url
    identity = "|".join(
        part
        for part in (recruitment_url or official_url, company_name, job_title, location)
        if part
    ) or "|".join(lines[:5])
    source_key = hashlib.sha256(identity.encode("utf-8")).hexdigest()

    return {
        "source_site": "givemeoc",
        "source_page": source_page,
        "source_key": source_key,
        "company_name": _truncate(company_name, 255),
        "job_title": _truncate(job_title, 255),
        "location": _truncate(location, 255),
        "target_candidates": _truncate(target_candidates, 255),
        "position": _truncate(position, 255),
        "progress_status": _truncate(progress_status, 255),
        "deadline": _truncate(deadline, 255),
        "official_url": _truncate(official_url, 1024),
        "recruitment_url": _truncate(recruitment_url, 1024),
        "summary": _truncate(text, 2000),
        "raw_html": _truncate(raw_html, 65000),
    }


def _extract_col(block: str, class_name: str) -> str | None:
    pattern = re.compile(
        rf"<td\b[^>]*class=[\"'][^\"']*\b{re.escape(class_name)}\b[^\"']*[\"'][^>]*>"
        r"(?P<html>.*?)</td>",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(block)
    if not match:
        return None
    return _strip_html(match.group("html"))


def _extract_attr(block: str, attr_name: str) -> str | None:
    pattern = re.compile(
        rf"\b{re.escape(attr_name)}=[\"'](?P<value>.*?)[\"']",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(block)
    if not match:
        return None
    return html.unescape(match.group("value")).strip()


def _strip_html(value: str) -> str | None:
    parser = TextAndLinkParser()
    parser.feed(value)
    text = parser.text
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(?:-|会员可见|Member only)$", "", text, flags=re.IGNORECASE)
    return text or None


def _extract_labeled_value(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        pattern = re.compile(
            rf"{re.escape(label)}\s*[:：]\s*([^\n|/]+)", re.IGNORECASE
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def _guess_company(lines: list[str]) -> str | None:
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in TITLE_KEYWORDS):
            continue
        if 2 <= len(line) <= 80:
            return line
    return lines[0] if lines else None


def _guess_title(lines: list[str]) -> str | None:
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in TITLE_KEYWORDS):
            return line
    return lines[1] if len(lines) > 1 else None


def _pick_official_url(links: list[str]) -> str | None:
    for link in links:
        if "givemeoc.com" not in link:
            return link
    return links[0] if links else None


def _pick_recruitment_url(links: list[str]) -> str | None:
    for link in links:
        lower = link.lower()
        if any(keyword in lower for keyword in LINK_KEYWORDS):
            return link
    return None


def _clean_links(links: list[str]) -> list[str]:
    cleaned = []
    seen = set()
    for link in links:
        if link.startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        if link not in seen:
            seen.add(link)
            cleaned.append(link)
    return cleaned


def _text_lines(text: str) -> list[str]:
    text = re.sub(r"\s*\|\s*", "\n", text)
    return [
        line.strip(" -\t")
        for line in re.split(r"[\n。]+", text)
        if 2 <= len(line.strip(" -\t")) <= 200
    ]


def _dedupe_jobs(jobs: list[dict]) -> list[dict]:
    deduped = []
    seen = set()
    for job in jobs:
        if job["source_key"] in seen:
            continue
        seen.add(job["source_key"])
        deduped.append(job)
    return deduped


def _truncate(value: str | None, max_length: int) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return value[:max_length]
