# author: sawyer-shi

import json
import logging
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils import get_api_token

logger = logging.getLogger(__name__)


class ElementDeleteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Delete custom element (subject)."""
        logger.info("Starting element delete task")

        try:
            api_token = get_api_token(self.runtime)
        except Exception as exc:
            msg = f"❌ 凭证获取失败: {exc}"
            logger.error(msg)
            yield self.create_text_message(msg)
            return

        element_id = (tool_parameters.get("element_id") or "").strip()
        if not element_id:
            msg = "❌ 请输入 element_id"
            logger.warning(msg)
            yield self.create_text_message(msg)
            return

        api_url = "https://api-beijing.klingai.com/v1/general/delete-elements"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        payload = {"element_id": element_id}

        yield self.create_text_message("🚀 主体删除任务启动中...")
        yield self.create_text_message(f"🧩 主体ID: {element_id}")

        try:
            logger.info("Submitting element delete payload: %s", json.dumps(payload, ensure_ascii=False))
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        except requests.exceptions.Timeout:
            msg = "❌ 请求超时，请稍后重试"
            logger.error(msg)
            yield self.create_text_message(msg)
            return
        except requests.exceptions.RequestException as exc:
            msg = f"❌ 请求失败: {exc}"
            logger.error(msg)
            yield self.create_text_message(msg)
            return

        if response.status_code != 200:
            logger.error("API status %s: %s", response.status_code, response.text[:300])
            yield self.create_text_message(f"❌ API 响应状态码: {response.status_code}")
            if response.text:
                yield self.create_text_message(f"🔧 响应内容: {response.text[:500]}")
            return

        try:
            resp_data = response.json()
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON: %s", exc)
            yield self.create_text_message("❌ API 响应解析失败（非JSON）")
            return

        if resp_data.get("code") != 0:
            msg = f"❌ 删除失败: {resp_data.get('message', '未知错误')}"
            logger.error(msg)
            yield self.create_text_message(msg)
            yield self.create_json_message(resp_data)
            return

        yield self.create_text_message("✅ 主体删除任务已提交")
        yield self.create_json_message(resp_data)
