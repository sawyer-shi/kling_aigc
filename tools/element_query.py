# author: sawyer-shi

import json
import logging
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils import format_timestamp, get_api_token, resolve_task_id

logger = logging.getLogger(__name__)


class ElementQueryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Query custom element (single)."""
        logger.info("Starting element query task")

        try:
            api_token = get_api_token(self.runtime)
        except Exception as exc:
            msg = f"❌ 凭证获取失败: {exc}"
            logger.error(msg)
            yield self.create_text_message(msg)
            return

        try:
            task_id = resolve_task_id(tool_parameters)
        except ValueError as exc:
            msg = str(exc)
            logger.warning(msg)
            yield self.create_text_message(msg)
            return

        api_url = f"https://api-beijing.klingai.com/v1/general/advanced-custom-elements/{task_id}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        yield self.create_text_message("🔍 正在查询主体任务...")
        yield self.create_text_message(f"📋 任务ID: {task_id}")

        try:
            response = requests.get(api_url, headers=headers, timeout=60)
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
            resp_data = json.loads(response.text, parse_int=str)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON: %s", exc)
            yield self.create_text_message("❌ API 响应解析失败（非JSON）")
            return

        code = resp_data.get("code")
        if str(code) != "0":
            msg = f"❌ 查询失败: {resp_data.get('message', '未知错误')}"
            logger.error(msg)
            yield self.create_text_message(msg)
            yield self.create_json_message(resp_data)
            return

        data = resp_data.get("data", {})
        task_status = data.get("task_status")
        task_status_msg = data.get("task_status_msg")
        created_at = format_timestamp(data.get("created_at"))
        updated_at = format_timestamp(data.get("updated_at"))
        task_result = data.get("task_result")

        yield self.create_text_message("✅ 查询成功")
        yield self.create_text_message(f"📊 状态: {task_status}")
        if task_status_msg:
            yield self.create_text_message(f"🧾 状态说明: {task_status_msg}")
        yield self.create_text_message(f"🕒 创建时间: {created_at}")
        yield self.create_text_message(f"🕒 更新时间: {updated_at}")

        element_source = None
        if isinstance(task_result, dict):
            elements = task_result.get("elements")
            if isinstance(elements, list) and elements:
                element_source = elements[0]
            else:
                element_source = task_result
        elif isinstance(data, dict):
            element_source = data

        if isinstance(element_source, dict):
            element_id = element_source.get("element_id")
            element_name = element_source.get("element_name")
            element_description = element_source.get("element_description")
            reference_type = element_source.get("reference_type") or element_source.get(
                "element_type"
            )
            owned_by = element_source.get("owned_by")
            status = element_source.get("status")
            if element_id:
                yield self.create_text_message(f"🧩 主体ID: {element_id}")
            if element_name:
                yield self.create_text_message(f"🏷️ 主体名称: {element_name}")
            if element_description:
                yield self.create_text_message(f"📝 主体描述: {element_description}")
            if reference_type:
                yield self.create_text_message(f"🔧 参考类型: {reference_type}")
            if status:
                yield self.create_text_message(f"✅ 主体状态: {status}")
            if owned_by:
                yield self.create_text_message(f"👤 来源: {owned_by}")
            if not any(
                [
                    element_id,
                    element_name,
                    element_description,
                    reference_type,
                    owned_by,
                    status,
                ]
            ):
                yield self.create_text_message("ℹ️ 响应中未包含主体详细信息")

        yield self.create_json_message(resp_data)
