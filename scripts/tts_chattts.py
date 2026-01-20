#!/usr/bin/env python3
"""
中文配音生成脚本 - 使用 ChatTTS (本地运行，完全免费)
用法: python tts_chattts.py <chinese.srt> [output.mp3]

首次运行会自动下载模型 (~1GB)
"""

import sys
import os
import tempfile
import subprocess
import pysrt
import torch
import ChatTTS
import torchaudio
import numpy as np

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

def generate_tts(
    input_srt: str,
    output_audio: str = None,
    seed: int = None,
):
    """从中文字幕生成配音 (使用 ChatTTS)"""

    # 读取字幕
    print(f"📖 读取字幕: {input_srt}")
    subs = pysrt.open(input_srt, encoding='utf-8')
    total = len(subs)
    print(f"   共 {total} 条字幕")

    # 初始化 ChatTTS
    print("🔧 加载 ChatTTS 模型 (首次需要下载)...")
    chat = ChatTTS.Chat()
    chat.load(compile=False)  # compile=True 可加速但首次编译慢

    # 设置说话人特征 (可固定 seed 保持声音一致)
    if seed is None:
        seed = 42  # 固定种子确保声音一致
    torch.manual_seed(seed)
    spk = chat.sample_random_speaker()
    print(f"   使用说话人种子: {seed}")

    # 参数设置
    params_infer = ChatTTS.Chat.InferCodeParams(
        spk_emb=spk,
        temperature=0.3,  # 较低温度更稳定
        top_P=0.7,
        top_K=20,
    )
    params_refine = ChatTTS.Chat.RefineTextParams(
        prompt='[oral_2][laugh_0][break_4]',  # 口语化，少笑声，适当停顿
    )

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    audio_segments = []

    # 收集所有文本
    texts = []
    sub_info = []
    for i, sub in enumerate(subs, start=1):
        text = sub.text.replace('\n', ' ').strip()
        if text:
            texts.append(text)
            sub_info.append((i, sub))

    # 批量生成语音 (ChatTTS 支持批量处理)
    print(f"🎙️ 生成配音中... (共 {len(texts)} 条)")
    batch_size = 10  # 每批处理数量

    for batch_start in range(0, len(texts), batch_size):
        batch_end = min(batch_start + batch_size, len(texts))
        batch_texts = texts[batch_start:batch_end]
        batch_info = sub_info[batch_start:batch_end]

        print(f"   处理 {batch_start + 1}-{batch_end}/{len(texts)}...")

        try:
            wavs = chat.infer(
                batch_texts,
                params_infer_code=params_infer,
                params_refine_text=params_refine,
            )

            for j, (wav, (idx, sub)) in enumerate(zip(wavs, batch_info)):
                segment_path = os.path.join(temp_dir, f"segment_{idx:04d}.wav")

                # ChatTTS 输出是 numpy array，采样率 24000
                wav_tensor = torch.from_numpy(wav).unsqueeze(0)
                torchaudio.save(segment_path, wav_tensor, 24000)

                audio_segments.append({
                    "path": segment_path,
                    "start_ms": sub.start.ordinal,
                    "text": batch_texts[j],
                })

        except Exception as e:
            print(f"⚠️ 批次处理失败: {e}")
            continue

    if not audio_segments:
        print("❌ 没有成功生成任何音频")
        sys.exit(1)

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
        print("用法: python tts_chattts.py <chinese.srt> [output.mp3] [seed]")
        print("\n参数说明:")
        print("  seed: 说话人种子，不同数字产生不同声音 (默认: 42)")
        print("\n示例:")
        print("  python tts_chattts.py subtitles_zh.srt output.mp3 42")
        sys.exit(1)

    input_srt = sys.argv[1]
    output_audio = sys.argv[2] if len(sys.argv) > 2 else None
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42

    generate_tts(input_srt, output_audio, seed)

if __name__ == "__main__":
    main()
