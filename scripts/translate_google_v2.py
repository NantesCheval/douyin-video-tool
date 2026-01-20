#!/usr/bin/env python3
"""
字幕翻译脚本 V2 - 改进的上下文感知翻译
特点：
1. 合并分段句子以保持上下文
2. 使用标点符号智能断句
3. 翻译后按时间重新分配

用法: python translate_google_v2.py <input.srt> [output.srt]
"""

import sys
import os
import time
import re
import pysrt
from deep_translator import GoogleTranslator


def is_sentence_end(text: str) -> bool:
    """检查文本是否以句子结束符结尾"""
    text = text.strip()
    if not text:
        return True
    # 英文句子结束符
    return text[-1] in '.?!。？！'


def merge_subtitle_groups(subs) -> list:
    """将相邻的字幕合并成完整句子组"""
    groups = []  # [(start_idx, end_idx, merged_text)]

    i = 0
    while i < len(subs):
        start_idx = i
        merged_text = subs[i].text.replace('\n', ' ').strip()

        # 继续合并直到遇到句子结束
        while i < len(subs) - 1 and not is_sentence_end(merged_text):
            i += 1
            next_text = subs[i].text.replace('\n', ' ').strip()
            merged_text = merged_text + ' ' + next_text

        groups.append((start_idx, i, merged_text))
        i += 1

    return groups


def split_translation(original_texts: list, translated_text: str) -> list:
    """根据原文的比例分割翻译结果"""
    if len(original_texts) == 1:
        return [translated_text]

    # 计算每段原文的长度比例
    total_len = sum(len(t) for t in original_texts)
    ratios = [len(t) / total_len for t in original_texts]

    # 按比例分割翻译（基于字符数）
    trans_len = len(translated_text)
    results = []
    start = 0

    for i, ratio in enumerate(ratios):
        if i == len(ratios) - 1:
            # 最后一段取剩余所有
            results.append(translated_text[start:].strip())
        else:
            # 按比例计算结束位置
            end = start + int(trans_len * ratio)

            # 找到最近的标点符号或空格作为分割点
            # 优先在标点处分割
            best_split = end
            for offset in range(min(15, end - start)):
                check_pos = end - offset
                if check_pos > start and translated_text[check_pos - 1] in '，。！？、；：':
                    best_split = check_pos
                    break
                check_pos = end + offset
                if check_pos < trans_len and translated_text[check_pos - 1] in '，。！？、；：':
                    best_split = check_pos
                    break

            results.append(translated_text[start:best_split].strip())
            start = best_split

    # 确保没有空结果
    results = [r if r else '...' for r in results]
    return results


def translate_subtitles(input_file: str, output_file: str = None):
    """使用上下文感知的方式翻译 SRT 字幕文件"""

    translator = GoogleTranslator(source='en', target='zh-CN')

    # 读取字幕
    print(f"📖 读取字幕: {input_file}")
    subs = pysrt.open(input_file)
    total = len(subs)
    print(f"   共 {total} 条字幕")

    # 合并相邻字幕成句子组
    print(f"🔗 分析句子结构...")
    groups = merge_subtitle_groups(subs)
    print(f"   合并为 {len(groups)} 个句子组")

    # 翻译每个句子组
    print(f"🔄 使用 Google Translate 翻译...")
    translations = {}  # idx -> translated_text

    for group_idx, (start_idx, end_idx, merged_text) in enumerate(groups):
        if (group_idx + 1) % 10 == 0:
            print(f"   处理句子组 {group_idx + 1}/{len(groups)}...")

        try:
            # 翻译合并后的句子
            translated = translator.translate(merged_text)

            if start_idx == end_idx:
                # 单条字幕，直接使用翻译结果
                translations[start_idx] = translated
            else:
                # 多条字幕合并的，需要分割
                original_texts = [subs[i].text.replace('\n', ' ').strip()
                                  for i in range(start_idx, end_idx + 1)]
                split_results = split_translation(original_texts, translated)

                for i, idx in enumerate(range(start_idx, end_idx + 1)):
                    translations[idx] = split_results[i]

        except Exception as e:
            print(f"⚠️ 翻译失败 (组 {group_idx}): {e}")
            # 保留原文
            for idx in range(start_idx, end_idx + 1):
                translations[idx] = subs[idx].text

        time.sleep(0.3)  # 避免请求太频繁

    # 更新字幕
    for idx, trans_text in translations.items():
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
        print("用法: python translate_google_v2.py <input.srt> [output.srt]")
        print("\n特点：")
        print("  - 合并分段句子以保持上下文")
        print("  - 智能断句，翻译质量更高")
        print("  - 无需 API key，完全免费")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    translate_subtitles(input_file, output_file)
