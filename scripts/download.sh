#!/bin/bash
# 科普视频下载脚本
# 用法: ./download.sh <YouTube视频URL>

set -e

VIDEO_URL="$1"
DOWNLOAD_DIR="$HOME/douyin-video-tool/downloads"

if [ -z "$VIDEO_URL" ]; then
    echo "用法: ./download.sh <YouTube视频URL>"
    echo "示例: ./download.sh https://www.youtube.com/watch?v=xxxxx"
    exit 1
fi

echo "📥 开始下载视频..."
echo "URL: $VIDEO_URL"
echo "保存目录: $DOWNLOAD_DIR"
echo ""

# 下载视频（最高质量）+ 英文字幕
yt-dlp \
    --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
    --merge-output-format mp4 \
    --write-sub \
    --write-auto-sub \
    --sub-lang "en,en-US,en-GB" \
    --sub-format "srt/vtt/best" \
    --convert-subs srt \
    --output "$DOWNLOAD_DIR/%(title)s.%(ext)s" \
    --restrict-filenames \
    --no-playlist \
    "$VIDEO_URL"

echo ""
echo "✅ 下载完成！"
echo "文件保存在: $DOWNLOAD_DIR"
ls -la "$DOWNLOAD_DIR"
