#!/usr/bin/env python3
"""
中文配音生成脚本 - 使用OpenAI TTS从中文字幕生成配音
用法: python tts.py <chinese.srt> [output.mp3]
"""

import sys
import os
import tempfile
import subprocess
import pysrt
from openai import OpenAI

def run_command(cmd, description):
    """执行命令并在失败时退出"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 失败: {description}")
        if result.stderr:
            print(result.stderr)
        sys.exit(1)
    return result

def mix_segments_with_timestamps(audio_segments, output_audio, temp_dir):
    """按字幕时间轴合并音频片段"""
    if not audio_segments:
        print("❌ 没有可用的音频片段")
        sys.exit(1)

    filter_lines = []
    mix_inputs = []
    for idx, seg in enumerate(audio_segments):
        delay_ms = max(0, int(seg["start_ms"]))
        filter_lines.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a{idx}]")
        mix_inputs.append(f"[a{idx}]")

    filter_lines.append(
        "".join(mix_inputs)
        + f"amix=inputs={len(audio_segments)}:duration=longest:normalize=0[aout]"
    )

    filter_script = os.path.join(temp_dir, "mix.ffmpeg")
    with open(filter_script, "w") as f:
        f.write(";".join(filter_lines))

    cmd = ["ffmpeg", "-y"]
    for seg in audio_segments:
        cmd.extend(["-i", seg["path"]])
    cmd.extend([
        "-filter_complex_script", filter_script,
        "-map", "[aout]",
        "-c:a", "mp3",
        output_audio,
    ])
    run_command(cmd, "合并音频片段")

def generate_tts(input_srt: str, output_audio: str = None, voice: str = "alloy"):
    """从中文字幕生成配音"""

    # 检查API Key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误: 请设置 OPENAI_API_KEY 环境变量")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # 读取字幕
    print(f"📖 读取字幕: {input_srt}")
    subs = pysrt.open(input_srt, encoding='utf-8')
    total = len(subs)
    print(f"   共 {total} 条字幕")
    print(f"   使用声音: {voice}")

    # 创建临时目录存放片段
    temp_dir = tempfile.mkdtemp()
    audio_segments = []

    for i, sub in enumerate(subs):
        text = sub.text.replace('\n', ' ').strip()
        if not text:
            continue

        print(f"🎙️ 生成配音... {i+1}/{total}")

        # 调用OpenAI TTS
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )

        # 保存片段
        segment_path = os.path.join(temp_dir, f"segment_{i:04d}.mp3")
        response.stream_to_file(segment_path)

        # 记录时间信息
        start_ms = sub.start.ordinal
        audio_segments.append({
            "path": segment_path,
            "start_ms": start_ms,
            "text": text
        })

    # 合并音频（使用ffmpeg按时间轴对齐）
    if output_audio is None:
        base, _ = os.path.splitext(input_srt)
        output_audio = f"{base}_audio.mp3"

    print("🔧 合并音频片段（按字幕时间轴）...")
    mix_segments_with_timestamps(audio_segments, output_audio, temp_dir)
    print(f"✅ 配音完成: {output_audio}")

    # 清理临时文件
    import shutil
    shutil.rmtree(temp_dir)

    return output_audio

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python tts.py <chinese.srt> [output.mp3] [voice]")
        print("可用声音: alloy(默认), echo, fable, onyx, nova, shimmer")
        sys.exit(1)

    input_srt = sys.argv[1]
    output_audio = sys.argv[2] if len(sys.argv) > 2 else None
    voice = sys.argv[3] if len(sys.argv) > 3 else "alloy"

    generate_tts(input_srt, output_audio, voice)
