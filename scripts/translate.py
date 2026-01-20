#!/usr/bin/env python3
"""
字幕翻译脚本 - 使用OpenAI API将英文SRT字幕翻译为中文
用法: python translate.py <input.srt> [output.srt]
"""

import sys
import os
import pysrt
from openai import OpenAI

def translate_subtitles(input_file: str, output_file: str = None):
    """翻译SRT字幕文件"""

    # 检查API Key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误: 请设置 OPENAI_API_KEY 环境变量")
        print("   export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # 读取字幕
    print(f"📖 读取字幕: {input_file}")
    subs = pysrt.open(input_file)
    total = len(subs)
    print(f"   共 {total} 条字幕")

    # 批量翻译（每10条一批，减少API调用次数）
    batch_size = 10
    translated_texts = []

    for i in range(0, total, batch_size):
        batch = subs[i:i+batch_size]
        texts = [sub.text.replace('\n', ' ') for sub in batch]

        # 构建翻译提示
        prompt = "将以下英文字幕翻译成简体中文，保持口语化、自然流畅。每行对应翻译，用换行分隔：\n\n"
        prompt += "\n".join([f"{j+1}. {t}" for j, t in enumerate(texts)])

        print(f"🔄 翻译中... {min(i+batch_size, total)}/{total}")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是专业的科普视频字幕翻译，翻译要准确、通俗易懂。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        # 解析翻译结果
        result = response.choices[0].message.content.strip()
        lines = result.split('\n')

        for line in lines:
            # 去掉序号前缀
            text = line.strip()
            if text and text[0].isdigit():
                text = text.split('.', 1)[-1].strip()
            if text:
                translated_texts.append(text)

    # 更新字幕
    for i, sub in enumerate(subs):
        if i < len(translated_texts):
            sub.text = translated_texts[i]

    # 保存
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_zh{ext}"

    subs.save(output_file, encoding='utf-8')
    print(f"✅ 翻译完成: {output_file}")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python translate.py <input.srt> [output.srt]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    translate_subtitles(input_file, output_file)
