from typing import Any

import requests


class APIClient:
    def __init__(self, base_url: str, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> dict[str, Any]:
        r = requests.get(f"{self.base_url}/", timeout=10)
        r.raise_for_status()
        return r.json()

    def upload_pdfs(self, files: list[tuple[str, bytes]]) -> dict[str, Any]:
        payload = [("files", (name, data, "application/pdf")) for name, data in files]
        r = requests.post(f"{self.base_url}/upload", files=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def chat(self, query: str, top_k: int | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"query": query}
        if top_k is not None:
            body["top_k"] = top_k
        r = requests.post(f"{self.base_url}/chat", json=body, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def summary(self, query: str, top_k: int | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"query": query}
        if top_k is not None:
            body["top_k"] = top_k
        r = requests.post(f"{self.base_url}/summary", json=body, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def generate_mcq(
        self, topic: str, num_questions: int, difficulty: str
    ) -> dict[str, Any]:
        body = {
            "topic": topic,
            "num_questions": num_questions,
            "difficulty": difficulty,
        }
        r = requests.post(f"{self.base_url}/mcq", json=body, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
