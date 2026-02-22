# Kling AIGC

A Dify plugin that integrates Kling AI 3.0 models for video, image, and element generation workflows. Supports omni-video, text-to-video, image-to-video, omni-image, image generation, and element management with task-based queries.

## Version Information

- **Current Version**: v0.0.1
- **Release Date**: 2026-02-16
- **Compatibility**: Dify Plugin Framework
- **Python Version**: 3.12

### Version History
- **v0.0.1** (2026-02-16): Initial release with Kling 3.0 video/image/element tools

## Quick Start

1. Install the plugin in your Dify environment
2. Configure your Kling AI credentials (Access Key + Secret Key)
3. Create tasks and query results

## Key Features
<img width="360" height="949" alt="CN" src="https://github.com/user-attachments/assets/4e3b8700-8081-455a-b995-f51f44ea9781" /><img width="358" height="954" alt="EN" src="https://github.com/user-attachments/assets/246727be-6476-47cb-ab72-8460d2fec768" />

- **Video Generation**: Omni-video, text-to-video, image-to-video
- **Image Generation**: Omni-image and image generation tasks
- **Element Management**: Create, query, and delete custom elements
- **Task Queries**: Single-task query with optional auto-download
- **Watermark Control**: Optional watermark output

## Core Features

### Video Tools

- **Omni-Video Create**: Multi-shot or single-shot video creation
- **Text to Video**: Prompt-based video generation
- **Image to Video**: First-frame / tail-frame and mask support
- **Video Query**: Task status, URLs, and optional download

### Image Tools

- **Omni-Image Create**: Prompt-based single/series image generation
- **Image Generation**: Prompt and optional image reference
- **Image Query**: Task status, URLs, and optional download

### Element Tools

- **Element Create**: Custom subject creation (image/video reference)
- **Element Query**: Retrieve element status and details
- **Element Delete**: Remove custom elements

## Requirements

- Python 3.12
- Dify Platform access
- Kling AI API credentials (Access Key + Secret Key)
- Required Python packages (installed via requirements.txt):
  - dify_plugin>=0.2.0
  - requests>=2.31.0
  - PyJWT>=2.8.0
  - Pillow>=9.0.0

## Installation & Configuration

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure Kling AI credentials in plugin settings:
   - **Access Key**
   - **Secret Key**
3. Install the plugin in your Dify environment

## Notes

- Generated assets are retained for 30 days; download promptly
- Queries support auto-download toggles for media retrieval

## Developer Information

- **Author**: https://github.com/sawyer-shi
- **Email**: sawyer36@foxmail.com
- **License**: Apache License 2.0
- **Source Code**: https://github.com/sawyer-shi/kling_aigc
- **Support**: Through Dify platform and GitHub Issues
