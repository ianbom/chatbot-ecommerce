from typing import Protocol
from urllib import request
from urllib.parse import parse_qs, urlparse
import json
import mimetypes

from app.core.config import get_settings


class WahaClient(Protocol):
    def send_text(self, chat_id: str, message: str) -> dict[str, object]: ...
    def send_image(self, chat_id: str, image_url: str, caption: str | None = None) -> dict[str, object]: ...


class HttpWahaClient:
    def send_text(self, chat_id: str, message: str) -> dict[str, object]:
        settings = get_settings()
        url = f"{settings.waha_base_url.rstrip('/')}/api/sendText"
        payload = {
            "session": settings.waha_session,
            "chatId": normalize_chat_id(chat_id),
            "text": message,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": settings.waha_api_key.get_secret_value(),
        }
        req = request.Request(url, data=body, headers=headers, method="POST")
        with request.urlopen(req, timeout=15) as response:
            response_body = response.read().decode("utf-8")
        if not response_body:
            return {"status": "sent"}
        return json.loads(response_body)

    def send_image(self, chat_id: str, image_url: str, caption: str | None = None) -> dict[str, object]:
        settings = get_settings()
        url = f"{settings.waha_base_url.rstrip('/')}/api/sendImage"
        normalized_image_url = normalize_image_url(image_url)
        filename = image_filename(normalized_image_url)
        mimetype = mimetypes.guess_type(filename)[0] or "image/jpeg"
        payload = {
            "session": settings.waha_session,
            "chatId": normalize_chat_id(chat_id),
            "file": {
                "url": normalized_image_url,
                "filename": filename,
                "mimetype": mimetype,
            },
            "caption": caption or "",
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": settings.waha_api_key.get_secret_value(),
        }
        req = request.Request(url, data=body, headers=headers, method="POST")
        with request.urlopen(req, timeout=30) as response:
            response_body = response.read().decode("utf-8")
        if not response_body:
            return {"status": "sent"}
        return json.loads(response_body)


def normalize_chat_id(chat_id: str) -> str:
    if "@" in chat_id:
        return chat_id
    return f"{chat_id}@c.us"


def extract_phone(chat_id: str) -> str:
    return chat_id.split("@", 1)[0]


def normalize_image_url(image_url: str) -> str:
    parsed = urlparse(image_url)
    if parsed.netloc == "drive.google.com" and parsed.path.startswith("/file/d/"):
        parts = parsed.path.split("/")
        if len(parts) >= 4 and parts[3]:
            return f"https://drive.google.com/uc?export=download&id={parts[3]}"
    return image_url


def image_filename(image_url: str) -> str:
    parsed = urlparse(image_url)
    query = parse_qs(parsed.query)
    if "id" in query and query["id"]:
        return f"{query['id'][0]}.jpg"
    path_name = parsed.path.rsplit("/", 1)[-1]
    if path_name and "." in path_name:
        return path_name
    return "product-image.jpg"
