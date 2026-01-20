#!/usr/bin/env python3
"""
抖音科普视频一键处理工具 (完全免费版)
用法: python process_free.py <YouTube视频URL>

流程:
1. 下载视频和英文字幕
2. 翻译字幕为中文 (Google Translate - 免费)
3. 生成中文配音 (ChatTTS 或 Edge TTS)
4. 合并为最终视频（中文配音 + 中文字幕）

无需任何 API key！
"""

import sys
import os
import subprocess
import glob
import argparse

# 项目目录
PROJECT_DIR = os.path.expanduser("~/douyin-video-tool")
DOWNLOAD_DIR = os.path.join(PROJECT_DIR, "downloads")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "scripts")
VENV_PYTHON = os.path.join(PROJECT_DIR, "venv/bin/python")

# Edge TTS 可用声音
EDGE_VOICES = ["xiaoxiao", "xiaoyi", "yunjian", "yunxi", "yunxia", "yunyang"]

def run_command(cmd, description):
    """执行命令并打印状态"""
    print(f"\n{'='*50}")
    print(f"🔹 {description}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str))
    if result.returncode != 0:
        print(f"❌ 失败: {description}")
        sys.exit(1)
    return result

def find_latest_file(directory, pattern):
    """找到目录中最新的匹配文件"""
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def main():
    parser = argparse.ArgumentParser(description='抖音科普视频一键处理工具 (完全免费版)')
    parser.add_argument('url', help='YouTube视频URL')
    parser.add_argument('--tts', default='edge', choices=['edge', 'chattts'],
                        help='TTS引擎: edge (快速，需联网) 或 chattts (高质量，需下载模型) (默认: edge)')
    parser.add_argument('--voice', default='yunxi',
                        help='Edge TTS声音: xiaoxiao/xiaoyi/yunjian/yunxi/yunxia/yunyang (默认: yunxi)')
    parser.add_argument('--seed', type=int, default=42,
                        help='ChatTTS 说话人种子，不同数字产生不同声音 (默认: 42)')
    parser.add_argument('--skip-download', action='store_true', help='跳过下载步骤')
    parser.add_argument('--browser', default='chrome', choices=['chrome', 'safari', 'firefox', 'edge'],
                        help='用于获取cookies的浏览器 (默认: chrome)')
    args = parser.parse_args()

    # 确保目录存在
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: 下载视频
    if not args.skip_download:
        run_command(
            f"yt-dlp --cookies-from-browser {args.browser} "
            f"--format 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' "
            f"--merge-output-format mp4 --write-sub --write-auto-sub "
            f"--sub-lang 'en,en-US,en-GB' --sub-format 'srt/vtt/best' --convert-subs srt "
            f"--output '{DOWNLOAD_DIR}/%(title)s.%(ext)s' --restrict-filenames --no-playlist "
            f"'{args.url}'",
            "下载视频和字幕"
        )

    # 查找下载的文件
    video_file = find_latest_file(DOWNLOAD_DIR, "*.mp4")
    srt_file = find_latest_file(DOWNLOAD_DIR, "*.srt")

    if not video_file:
        print("❌ 未找到视频文件")
        sys.exit(1)

    if not srt_file:
        print("⚠️ 未找到字幕文件，请手动添加或使用Whisper生成")
        sys.exit(1)

    print(f"\n📁 视频文件: {video_file}")
    print(f"📁 字幕文件: {srt_file}")

    # Step 2: 翻译字幕 (使用 Google Translate V2 - 上下文感知翻译)
    base_name = os.path.splitext(os.path.basename(video_file))[0]
    chinese_srt = os.path.join(DOWNLOAD_DIR, f"{base_name}_zh.srt")

    run_command(
        [VENV_PYTHON, os.path.join(SCRIPTS_DIR, "translate_google_v2.py"), srt_file, chinese_srt],
        "翻译字幕为中文 (Google Translate - 上下文感知)"
    )

    # Step 3: 生成配音
    chinese_audio = os.path.join(DOWNLOAD_DIR, f"{base_name}_zh.mp3")

    if args.tts == 'chattts':
        run_command(
            [VENV_PYTHON, os.path.join(SCRIPTS_DIR, "tts_chattts.py"), chinese_srt, chinese_audio, str(args.seed)],
            "生成中文配音 (ChatTTS - 高质量)"
        )
    else:
        # 默认使用 Edge TTS
        voice = args.voice if args.voice in EDGE_VOICES else 'yunxi'
        run_command(
            [VENV_PYTHON, os.path.join(SCRIPTS_DIR, "tts_free.py"), chinese_srt, chinese_audio, voice],
            f"生成中文配音 (Edge TTS - {voice})"
        )

    # Step 4: 合并视频
    output_video = os.path.join(OUTPUT_DIR, f"{base_name}_final.mp4")

    # 使用ffmpeg合并：视频轨 + 中文音频
    run_command(
        [
            "ffmpeg", "-y",
            "-i", video_file,
            "-i", chinese_audio,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            output_video
        ],
        "合并视频（视频+中文配音）"
    )

    # 复制字幕到输出目录
    output_srt = os.path.join(OUTPUT_DIR, f"{base_name}_zh.srt")
    import shutil
    shutil.copy2(chinese_srt, output_srt)

    # Step 5: 烧录字幕到视频
    output_with_subs = os.path.join(OUTPUT_DIR, f"{base_name}_with_subs.mp4")
    run_command(
        [VENV_PYTHON, os.path.join(SCRIPTS_DIR, "burn_subtitles.py"),
         output_video, output_srt, output_with_subs],
        "烧录中文字幕到视频"
    )

    print(f"\n{'='*50}")
    print(f"🎉 处理完成！")
    print(f"{'='*50}")
    print(f"📁 无字幕视频: {output_video}")
    print(f"📁 带字幕视频: {output_with_subs}")
    print(f"📁 字幕文件: {output_srt}")
    print(f"\n下一步:")
    print(f"1. 用剪映打开带字幕视频")
    print(f"2. 调整为9:16竖屏（裁剪或添加背景）")
    print(f"3. 添加片头片尾")
    print(f"4. 发布到抖音")

if __name__ == "__main__":
    main()
