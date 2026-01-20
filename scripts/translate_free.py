#!/usr/bin/env python3
"""
字幕翻译脚本（免费版）- 使用MyMemory翻译API
用法: python translate_free.py <input.srt> [output.srt]
"""

import sys
import os
import time
import pysrt
from deep_translator import MyMemoryTranslator

def translate_subtitles(input_file: str, output_file: str = None):
    """翻译SRT字幕文件"""

    translator = MyMemoryTranslator(source='en-US', target='zh-CN')

    # 读取字幕
    print(f"📖 读取字幕: {input_file}")
    subs = pysrt.open(input_file)
    total = len(subs)
    print(f"   共 {total} 条字幕")

    # 逐条翻译
    for i, sub in enumerate(subs):
        text = sub.text.replace('\n', ' ').strip()
        if not text:
            continue

        print(f"🔄 翻译中... {i+1}/{total}")

        try:
            result = translator.translate(text)
            if result:
                sub.text = result
        except Exception as e:
            print(f"⚠️ 跳过 ({i+1}): {e}")

        time.sleep(0.5)  # 避免请求太频繁

    print(f"✅ 翻译完成")

    # 保存
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_zh{ext}"

    subs.save(output_file, encoding='utf-8')
    print(f"📁 保存到: {output_file}")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python translate_free.py <input.srt> [output.srt]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    translate_subtitles(input_file, output_file)
