#!/usr/bin/env python3
"""
字幕翻译脚本 - 使用 Google Translate (完全免费，无需 API key)
用法: python translate_google.py <input.srt> [output.srt]
"""

import sys
import os
import time
import pysrt
from deep_translator import GoogleTranslator

def translate_subtitles(input_file: str, output_file: str = None):
    """使用 Google Translate 翻译 SRT 字幕文件"""

    translator = GoogleTranslator(source='en', target='zh-CN')

    # 读取字幕
    print(f"📖 读取字幕: {input_file}")
    subs = pysrt.open(input_file)
    total = len(subs)
    print(f"   共 {total} 条字幕")

    # 收集所有文本
    texts = []
    indices = []
    for i, sub in enumerate(subs):
        text = sub.text.replace('\n', ' ').strip()
        if text:
            texts.append(text)
            indices.append(i)

    print(f"🔄 使用 Google Translate 批量翻译 {len(texts)} 条字幕...")

    # 分批翻译（每批最多 30 条，避免请求过大）
    batch_size = 30
    translated = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size
        print(f"   翻译批次 {batch_num}/{total_batches}...")

        try:
            # Google Translate 支持批量翻译
            results = translator.translate_batch(batch)
            translated.extend(results)
        except Exception as e:
            print(f"⚠️ 批次翻译失败，尝试逐条翻译: {e}")
            # 失败时逐条翻译
            for text in batch:
                try:
                    result = translator.translate(text)
                    translated.append(result)
                except Exception as e2:
                    print(f"⚠️ 跳过: {e2}")
                    translated.append(text)  # 保留原文
                time.sleep(0.3)

        time.sleep(0.5)  # 避免请求太频繁

    # 更新字幕
    for idx, trans_text in zip(indices, translated):
        if trans_text:
            subs[idx].text = trans_text

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
        print("用法: python translate_google.py <input.srt> [output.srt]")
        print("\n无需 API key，完全免费")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    translate_subtitles(input_file, output_file)
