from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ALLOWED_DOMAINS = {"www.swedish.org", "swedish.org", "providenceswedishcancer.org", "www.providenceswedishcancer.org"}

@dataclass
class ScrapedPage:
    url: str
    title: str
    text: str


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"Unsupported URL scheme: {url}")
    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError(f"Domain not allowlisted for this demo: {parsed.netloc}")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(Back to Main Menu|Full Menu|current templateID).*?", "", text)
    return text.strip()


def fetch_page(url: str, timeout: int = 15) -> ScrapedPage:
    validate_url(url)
    headers = {"User-Agent": "educational-rag-demo/1.0"}
    response = requests.get(url, timeout=timeout, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else url
    main = soup.find("main") or soup.body or soup
    text = clean_text(main.get_text(" ", strip=True))
    return ScrapedPage(url=url, title=title, text=text)
