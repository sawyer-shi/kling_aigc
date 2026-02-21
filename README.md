# Kling AIGC

A Dify plugin that integrates Kling AI for video, image, and audio generation/editing. Includes task creation and query tools for text-to-video, image-to-video, multi-image video, effects, lip sync, audio generation, and image recognition.

## Version Information

- **Current Version**: v0.0.1
- **Release Date**: 2026-02-16
- **Compatibility**: Dify Plugin Framework
- **Python Version**: 3.12

## Quick Start

1. Install the plugin in your Dify environment
2. Configure your Kling AI credentials (Access Key + Secret Key)
3. Start creating and querying video/image/audio tasks

## Key Features

- **Text to Video**: Create and query Kling video tasks
- **Image to Video**: Single and multi-image video generation
- **Video Effects**: Effect creation and status query
- **Lip Sync**: Identify, create, and query lip sync tasks
- **Audio Tools**: Text-to-audio, video-to-audio, and TTS
- **Image Tools**: Image generation, expansion, and recognition

## Requirements

- Python 3.12
- Dify Platform access
- Kling AI API credentials (Access Key + Secret Key)
- Required Python packages (installed via requirements.txt):
  - dify_plugin>=0.2.0,<0.3.0
  - requests>=2.31.0
  - PyJWT>=2.8.0
  - Pillow>=9.0.0

## Support

- Refer to Kling AI documentation for API details
- Generated assets are retained for 30 days; download promptly
