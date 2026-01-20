---
name: douyin-video
description: 处理YouTube科普视频，自动下载、翻译字幕、生成中文配音。当用户提供YouTube链接并要求处理视频时使用。
allowed-tools:
  - Bash
  - Read
---

# 抖音科普视频处理工具 (完全免费版)

将YouTube科普视频自动转换为适合抖音发布的中文版本。**无需任何API key！**

## 功能

1. **下载视频** - 从YouTube下载最高画质视频和英文字幕
2. **翻译字幕** - 使用 Google Translate (上下文感知翻译，完全免费)
3. **生成配音** - 使用 Edge TTS 或 ChatTTS (完全免费)
4. **合成视频** - 将中文配音合并到视频中
5. **烧录字幕** - 将中文字幕硬编码到视频中

## 使用方法

### 处理视频

当用户提供YouTube URL时，执行以下命令：

```bash
~/douyin-video-tool/run.sh '<YouTube视频URL>'
```

### TTS 选项

```bash
# Edge TTS (默认，快速，需联网)
~/douyin-video-tool/run.sh 'URL' --tts edge --voice yunxi

# ChatTTS (高质量，首次需下载1GB模型)
~/douyin-video-tool/run.sh 'URL' --tts chattts --seed 42
```

### Edge TTS 可用声音

| 声音 | 说明 |
|------|------|
| `yunxi` | 男声，年轻 (默认) |
| `yunyang` | 男声，新闻播音风格 |
| `yunjian` | 男声，沉稳 |
| `xiaoxiao` | 女声，温柔 |
| `xiaoyi` | 女声，活泼 |

### 其他参数

- `--skip-download` - 跳过下载步骤（使用已下载的文件）
- `--browser <name>` - 浏览器 (chrome/safari/firefox/edge)

### 示例

```bash
# 基本用法
~/douyin-video-tool/run.sh 'https://www.youtube.com/watch?v=xxxxx'

# 使用不同声音
~/douyin-video-tool/run.sh 'https://www.youtube.com/watch?v=xxxxx' --voice yunyang

# 使用ChatTTS高质量配音
~/douyin-video-tool/run.sh 'https://www.youtube.com/watch?v=xxxxx' --tts chattts --seed 100
```

## 执行步骤

1. 检查用户是否提供了YouTube URL
2. 执行 `~/douyin-video-tool/run.sh` 命令处理视频
3. 等待处理完成（视频长度决定时间）
4. 告知用户输出文件位置：
   - 无字幕视频: `~/douyin-video-tool/output/xxx_final.mp4`
   - 带字幕视频: `~/douyin-video-tool/output/xxx_with_subs.mp4`
   - 字幕文件: `~/douyin-video-tool/output/xxx_zh.srt`
5. 提醒后续步骤：用剪映调整为竖屏、添加片头片尾、发布

## 目录结构

- `~/douyin-video-tool/downloads/` - 下载的原始视频和字幕
- `~/douyin-video-tool/output/` - 处理后的最终视频
- `~/douyin-video-tool/scripts/` - 处理脚本

## 技术栈

| 功能 | 技术 | 成本 |
|------|------|------|
| 视频下载 | yt-dlp | 免费 |
| 翻译 | Google Translate (上下文感知) | 免费 |
| TTS | Edge TTS / ChatTTS | 免费 |
| 视频处理 | ffmpeg | 免费 |
| 字幕烧录 | moviepy | 免费 |

## 推荐科普频道

- **Kurzgesagt** - 动画科普，画面精美
- **TED-Ed** - 教育动画
- **Veritasium** - 科学实验和解说
- **Mark Rober** - 工程和科学实验
- **3Blue1Brown** - 数学可视化
