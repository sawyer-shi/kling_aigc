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


class Text2VideoQueryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Kling text-to-video single task query."""
        logger.info("Starting text-to-video query task")

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

        download_video = tool_parameters.get("download_video", "false") == "true"

        api_url = f"https://api-beijing.klingai.com/v1/videos/text2video/{task_id}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        yield self.create_text_message("🔍 正在查询文生视频任务...")
        yield self.create_text_message(f"📋 任务ID: {task_id}")
        if download_video:
            yield self.create_text_message("⬇️ 下载选项已开启")

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
            resp_data = response.json()
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON: %s", exc)
            yield self.create_text_message("❌ API 响应解析失败（非JSON）")
            return

        if resp_data.get("code") != 0:
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
        task_result = data.get("task_result", {})
        videos = task_result.get("videos", []) if isinstance(task_result, dict) else []

        yield self.create_text_message("✅ 查询成功")
        yield self.create_text_message(f"📊 状态: {task_status}")
        if task_status_msg:
            yield self.create_text_message(f"🧾 状态说明: {task_status_msg}")
        yield self.create_text_message(f"🕒 创建时间: {created_at}")
        yield self.create_text_message(f"🕒 更新时间: {updated_at}")

        if videos:
            yield self.create_text_message("🎬 生成结果:")
            for idx, video in enumerate(videos, start=1):
                url = video.get("url")
                watermark_url = video.get("watermark_url")
                duration = video.get("duration")
                yield self.create_text_message(f"#{idx} 时长: {duration}s")
                if url:
                    yield self.create_text_message(f"链接: {url}")
                    if download_video:
                        yield self.create_text_message("⬇️ 正在下载视频文件...")
                        try:
                            video_response = requests.get(url, timeout=120)
                            if video_response.status_code == 200:
                                yield self.create_blob_message(
                                    blob=video_response.content,
                                    meta={
                                        "mime_type": "video/mp4",
                                        "filename": f"{task_id}_{idx}.mp4",
                                    },
                                )
                                yield self.create_text_message("✅ 视频下载完成")
                            else:
                                yield self.create_text_message(
                                    f"❌ 视频下载失败，状态码: {video_response.status_code}"
                                )
                        except requests.exceptions.RequestException as exc:
                            yield self.create_text_message(f"❌ 视频下载失败: {exc}")
                if watermark_url:
                    yield self.create_text_message(f"水印链接: {watermark_url}")
            yield self.create_text_message("⚠️ 生成的视频将于30天后清理，请及时转存")

        yield self.create_json_message(resp_data)
