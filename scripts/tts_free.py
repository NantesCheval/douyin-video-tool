#!/usr/bin/env python3
"""
中文配音生成脚本（免费版）- 使用Microsoft Edge TTS
用法: python tts_free.py <chinese.srt> [output.mp3]
"""

import sys
import os
import asyncio
import tempfile
import subprocess
import pysrt
import edge_tts

# 可用的中文声音
VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 女声，温柔
    "xiaoyi": "zh-CN-XiaoyiNeural",          # 女声，活泼
    "yunjian": "zh-CN-YunjianNeural",        # 男声，沉稳（推荐科普）
    "yunxi": "zh-CN-YunxiNeural",            # 男声，年轻
    "yunxia": "zh-CN-YunxiaNeural",          # 男声
    "yunyang": "zh-CN-YunyangNeural",        # 男声，新闻播音风格
}

async def generate_audio_segment(text: str, voice: str, output_path: str):
    """生成单条音频"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

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

async def generate_tts(
    input_srt: str,
    output_audio: str = None,
    voice_name: str = "yunxi",
    segment_timeout: int = 20,
    concurrency: int = 5,
):
    """从中文字幕生成配音"""

    voice = VOICES.get(voice_name, VOICES["yunxi"])

    # 读取字幕
    print(f"📖 读取字幕: {input_srt}")
    subs = pysrt.open(input_srt, encoding='utf-8')
    total = len(subs)
    print(f"   共 {total} 条字幕")
    print(f"   使用声音: {voice_name} ({voice})")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    audio_segments = []

    semaphore = asyncio.Semaphore(concurrency)

    async def synthesize_segment(index, sub, text, segment_path):
        async with semaphore:
            print(f"🎙️ 生成配音... {index}/{total}")
            try:
                await asyncio.wait_for(
                    generate_audio_segment(text, voice, segment_path),
                    timeout=segment_timeout
                )
                return {
                    "path": segment_path,
                    "start_ms": sub.start.ordinal,
                    "text": text,
                }
            except asyncio.TimeoutError:
                print(f"⚠️ 超时跳过 ({index})")
            except Exception as e:
                print(f"⚠️ 跳过 ({index}): {e}")
            return None

    tasks = []
    for i, sub in enumerate(subs, start=1):
        text = sub.text.replace('\n', ' ').strip()
        if not text:
            continue
        segment_path = os.path.join(temp_dir, f"segment_{i:04d}.mp3")
        tasks.append(asyncio.create_task(
            synthesize_segment(i, sub, text, segment_path)
        ))

    results = await asyncio.gather(*tasks)
    audio_segments = [seg for seg in results if seg is not None]

    # 合并音频
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

def main():
    if len(sys.argv) < 2:
        print("用法: python tts_free.py <chinese.srt> [output.mp3] [voice] [concurrency]")
        print("\n可用声音:")
        for name, voice in VOICES.items():
            print(f"  {name}: {voice}")
        sys.exit(1)

    input_srt = sys.argv[1]
    output_audio = sys.argv[2] if len(sys.argv) > 2 else None
    voice = sys.argv[3] if len(sys.argv) > 3 else "yunxi"
    concurrency = int(sys.argv[4]) if len(sys.argv) > 4 else 5

    asyncio.run(generate_tts(input_srt, output_audio, voice, concurrency=concurrency))

if __name__ == "__main__":
    main()
