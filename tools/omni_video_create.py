# author: sawyer-shi

import json
import logging
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils import (
    build_watermark_info,
    get_api_token,
    parse_json_param,
    resolve_files_to_list,
    resolve_media_input,
)

logger = logging.getLogger(__name__)


class OmniVideoCreateTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Kling Omni-Video create task."""
        logger.info("Starting omni-video create task")

        try:
            api_token = get_api_token(self.runtime)
        except Exception as exc:
            msg = f"❌ 凭证获取失败: {exc}"
            logger.error(msg)
            yield self.create_text_message(msg)
            return

        api_url = "https://api-beijing.klingai.com/v1/videos/omni-video"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        model_name = tool_parameters.get("model_name", "kling-video-o1")
        multi_shot = tool_parameters.get("multi_shot")
        shot_type = tool_parameters.get("shot_type")
        prompt = (tool_parameters.get("prompt") or "").strip()

        payload: dict[str, Any] = {
            "model_name": model_name,
        }

        if multi_shot is not None:
            payload["multi_shot"] = str(multi_shot).lower() == "true"
        if shot_type:
            payload["shot_type"] = shot_type
        if prompt:
            payload["prompt"] = prompt

        multi_prompt = parse_json_param(tool_parameters.get("multi_prompt"), "multi_prompt")
        if multi_prompt:
            payload["multi_prompt"] = multi_prompt

        image_list = tool_parameters.get("image_list")
        if image_list:
            if isinstance(image_list, list):
                payload["image_list"] = resolve_files_to_list(image_list, "image_url")
            else:
                parsed = parse_json_param(image_list, "image_list")
                if parsed:
                    payload["image_list"] = parsed

        element_list = parse_json_param(tool_parameters.get("element_list"), "element_list")
        if element_list:
            payload["element_list"] = element_list

        video_list = parse_json_param(tool_parameters.get("video_list"), "video_list")
        if video_list:
            payload["video_list"] = video_list

        sound = tool_parameters.get("sound")
        if sound:
            payload["sound"] = sound

        mode = tool_parameters.get("mode")
        if mode:
            payload["mode"] = mode

        aspect_ratio = tool_parameters.get("aspect_ratio")
        if aspect_ratio:
            payload["aspect_ratio"] = aspect_ratio

        duration = tool_parameters.get("duration")
        if duration:
            payload["duration"] = str(duration)

        watermark = build_watermark_info(tool_parameters.get("watermark"))
        if watermark:
            payload["watermark_info"] = watermark

        callback_url = tool_parameters.get("callback_url")
        if callback_url:
            payload["callback_url"] = callback_url

        external_task_id = tool_parameters.get("external_task_id")
        if external_task_id:
            payload["external_task_id"] = external_task_id

        yield self.create_text_message("🚀 Omni-Video 任务启动中...")
        yield self.create_text_message(f"🤖 模型: {model_name}")
        if prompt:
            yield self.create_text_message(
                f"📝 提示词: {prompt[:80]}{'...' if len(prompt) > 80 else ''}"
            )
        yield self.create_text_message("⏳ 正在连接可灵 AI API...")

        try:
            logger.info("Submitting omni-video payload: %s", json.dumps(payload, ensure_ascii=False))
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
        created_at = data.get("created_at")

        yield self.create_text_message("✅ Omni-Video 任务创建成功")
        if task_id:
            yield self.create_text_message(f"📋 任务ID: {task_id}")
        if task_status:
            yield self.create_text_message(f"📊 状态: {task_status}")
        if created_at:
            yield self.create_text_message(f"🕒 创建时间: {created_at}")
        yield self.create_text_message("💡 请使用 Omni-Video 查询工具获取结果")
        yield self.create_json_message(resp_data)
