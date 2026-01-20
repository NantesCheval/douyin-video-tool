#!/usr/bin/env python3
"""
字幕翻译脚本 - 使用 DeepL API (免费版)
用法: python translate_deepl.py <input.srt> [output.srt]

需要设置环境变量 DEEPL_API_KEY (免费版 key 也可以)
免费注册: https://www.deepl.com/pro#developer
"""

import sys
import os
import pysrt
import deepl

def translate_subtitles(input_file: str, output_file: str = None):
    """使用 DeepL 翻译 SRT 字幕文件"""

    api_key = os.environ.get("DEEPL_API_KEY")
    if not api_key:
        print("❌ 错误: 请设置 DEEPL_API_KEY 环境变量")
        print("   免费注册: https://www.deepl.com/pro#developer")
        sys.exit(1)

    translator = deepl.Translator(api_key)

    # 读取字幕
    print(f"📖 读取字幕: {input_file}")
    subs = pysrt.open(input_file)
    total = len(subs)
    print(f"   共 {total} 条字幕")

    # 收集所有文本进行批量翻译（DeepL 支持批量，效率更高）
    texts = []
    indices = []
    for i, sub in enumerate(subs):
        text = sub.text.replace('\n', ' ').strip()
        if text:
            texts.append(text)
            indices.append(i)

    print(f"🔄 使用 DeepL 批量翻译 {len(texts)} 条字幕...")

    # 分批翻译（每批最多50条，避免请求过大）
    batch_size = 50
    translated = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size
        print(f"   翻译批次 {batch_num}/{total_batches}...")

        try:
            results = translator.translate_text(batch, target_lang="ZH")
            for result in results:
                translated.append(result.text)
        except Exception as e:
            print(f"❌ 翻译失败: {e}")
            sys.exit(1)

    # 更新字幕
    for idx, trans_text in zip(indices, translated):
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
        print("用法: python translate_deepl.py <input.srt> [output.srt]")
        print("\n需要设置环境变量 DEEPL_API_KEY")
        print("免费注册: https://www.deepl.com/pro#developer")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    translate_subtitles(input_file, output_file)
