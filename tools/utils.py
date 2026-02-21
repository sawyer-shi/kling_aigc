# author: sawyer-shi

import base64
import json
import logging
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from provider.kling_aigc import KlingAigcProvider

logger = logging.getLogger(__name__)


def get_api_token(runtime) -> str:
    credentials = runtime.credentials
    return KlingAigcProvider.get_api_token(credentials)


def parse_json_param(value: Any, name: str) -> Optional[Any]:
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{name} 参数需要有效的 JSON 字符串") from exc
    raise ValueError(f"{name} 参数类型不支持")


def resolve_media_input(value: Any) -> Optional[str]:
    if value is None:
        return None
    if hasattr(value, "blob"):
        return base64.b64encode(value.blob).decode("utf-8")
    if hasattr(value, "read") and callable(getattr(value, "read")):
        data = value.read()
        if isinstance(data, str):
            data = data.encode("utf-8")
        return base64.b64encode(data).decode("utf-8")
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("utf-8")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.startswith("data:"):
            _, payload = text.split(",", 1)
            return payload
        return text
    return None


def resolve_files_to_list(
    files: Iterable[Any], field_name: str = "image_url"
) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for item in files:
        media = resolve_media_input(item)
        if media:
            result.append({field_name: media})
    return result


def parse_bool(value: Any, default: Optional[bool] = None) -> Optional[bool]:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes"}:
            return True
        if text in {"false", "0", "no"}:
            return False
    return default


def build_watermark_info(enabled: Any) -> Optional[dict[str, bool]]:
    flag = parse_bool(enabled)
    if flag is None:
        return None
    return {"enabled": flag}


def format_timestamp(timestamp_ms: Any) -> str:
    if not timestamp_ms:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(int(timestamp_ms) / 1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"


def resolve_task_id(tool_parameters: dict[str, Any]) -> str:
    task_id = (tool_parameters.get("task_id") or "").strip()
    external_task_id = (tool_parameters.get("external_task_id") or "").strip()
    if task_id:
        return task_id
    if external_task_id:
        return external_task_id
    raise ValueError("❌ 请输入 task_id 或 external_task_id")


def handle_credential_error(err: Exception) -> str:
    if isinstance(err, ToolProviderCredentialValidationError):
        return f"❌ 凭证错误: {err}"
    return f"❌ 凭证获取失败: {err}"
