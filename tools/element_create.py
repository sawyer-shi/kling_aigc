# author: sawyer-shi

import json
import logging
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils import get_api_token, parse_json_param, resolve_files_to_list, resolve_media_input

logger = logging.getLogger(__name__)


class ElementCreateTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Create custom element (subject)."""
        logger.info("Starting element create task")

        try:
            api_token = get_api_token(self.runtime)
        except Exception as exc:
            msg = f"❌ 凭证获取失败: {exc}"
            logger.error(msg)
            yield self.create_text_message(msg)
            return

        element_name = (tool_parameters.get("element_name") or "").strip()
        element_description = (tool_parameters.get("element_description") or "").strip()
        reference_type = (tool_parameters.get("reference_type") or "").strip()

        if not element_name or not element_description or not reference_type:
            msg = "❌ 请填写 element_name、element_description 和 reference_type"
            logger.warning(msg)
            yield self.create_text_message(msg)
            return

        api_url = "https://api-beijing.klingai.com/v1/general/advanced-custom-elements"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "element_name": element_name,
            "element_description": element_description,
            "reference_type": reference_type,
        }

        element_image_list = parse_json_param(
            tool_parameters.get("element_image_list"), "element_image_list"
        )
        if element_image_list:
            payload["element_image_list"] = element_image_list

        frontal_image = resolve_media_input(tool_parameters.get("element_frontal_image"))
        refer_images = tool_parameters.get("element_refer_images")
        refer_image_list = (
            resolve_files_to_list(refer_images, "image_url") if refer_images else []
        )
        if frontal_image or refer_image_list:
            payload["element_image_list"] = {
                "frontal_image": frontal_image,
                "refer_images": refer_image_list,
            }

        element_video_list = parse_json_param(
            tool_parameters.get("element_video_list"), "element_video_list"
        )
        if element_video_list:
            payload["element_video_list"] = element_video_list

        element_voice_id = tool_parameters.get("element_voice_id")
        if element_voice_id:
            payload["element_voice_id"] = element_voice_id

        tag_list = parse_json_param(tool_parameters.get("tag_list"), "tag_list")
        if tag_list:
            payload["tag_list"] = tag_list

        callback_url = tool_parameters.get("callback_url")
        if callback_url:
            payload["callback_url"] = callback_url

        external_task_id = tool_parameters.get("external_task_id")
        if external_task_id:
            payload["external_task_id"] = external_task_id

        yield self.create_text_message("🚀 主体创建任务启动中...")
        yield self.create_text_message(f"🏷️ 主体名称: {element_name}")
        yield self.create_text_message("⏳ 正在连接可灵 AI API...")

        try:
            logger.info("Submitting element create payload: %s", json.dumps(payload, ensure_ascii=False))
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
            msg = f"❌ 创建失败: {resp_data.get('message', '未知错误')}"
            logger.error(msg)
            yield self.create_text_message(msg)
            yield self.create_json_message(resp_data)
            return

        data = resp_data.get("data", {})
        task_id = data.get("task_id")
        task_status = data.get("task_status")

        yield self.create_text_message("✅ 主体创建任务已提交")
        if task_id:
            yield self.create_text_message(f"📋 任务ID: {task_id}")
        if task_status:
            yield self.create_text_message(f"📊 状态: {task_status}")
        yield self.create_text_message("💡 请使用主体查询工具获取结果")
        yield self.create_json_message(resp_data)
