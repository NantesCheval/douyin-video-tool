#!/usr/bin/env python3
"""
字幕烧录脚本 - 将 SRT 字幕烧录到视频中
用法: python burn_subtitles.py <video.mp4> <subtitles.srt> [output.mp4]
"""

import sys
import os
import pysrt
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def burn_subtitles(video_path: str, srt_path: str, output_path: str = None):
    """使用 moviepy 烧录字幕"""

    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_subtitled{ext}"

    print(f"📖 读取字幕: {srt_path}")
    subs = pysrt.open(srt_path, encoding='utf-8')
    total = len(subs)
    print(f"   共 {total} 条字幕")

    print(f"📹 加载视频: {video_path}")
    video = VideoFileClip(video_path)

    # 创建字幕剪辑列表
    subtitle_clips = []

    for i, sub in enumerate(subs, 1):
        if i % 10 == 0:
            print(f"   处理字幕 {i}/{total}...")

        start_time = sub.start.ordinal / 1000
        end_time = sub.end.ordinal / 1000
        duration = end_time - start_time

        text = sub.text.replace('\n', ' ')

        try:
            txt_clip = TextClip(
                text=text,
                font_size=48,
                color='white',
                stroke_color='black',
                stroke_width=2,
                font='/System/Library/Fonts/STHeiti Medium.ttc',
                method='caption',
                size=(int(video.w * 0.9), None),
            )
            txt_clip = txt_clip.with_start(start_time).with_duration(duration)
            txt_clip = txt_clip.with_position(('center', int(video.h - 120)))
            subtitle_clips.append(txt_clip)
        except Exception as e:
            print(f"⚠️ 跳过字幕 {i}: {e}")

    print(f"🔧 合成视频...")
    final = CompositeVideoClip([video] + subtitle_clips)

    print(f"💾 导出视频: {output_path}")
    final.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=video.fps,
        preset='fast',
        threads=4,
        logger=None
    )

    video.close()
    final.close()

    print(f"✅ 完成: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python burn_subtitles.py <video.mp4> <subtitles.srt> [output.mp4]")
        sys.exit(1)

    video_path = sys.argv[1]
    srt_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    burn_subtitles(video_path, srt_path, output_path)
