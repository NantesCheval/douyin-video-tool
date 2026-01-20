# 抖音科普视频处理工具

将 YouTube 科普视频自动转换为适合抖音发布的中文版本。**完全免费，无需任何 API key！**

## 功能

1. **下载视频** - 从 YouTube 下载最高画质视频和英文字幕
2. **翻译字幕** - 使用 Google Translate (上下文感知翻译)
3. **生成配音** - 使用 Edge TTS 或 ChatTTS
4. **合成视频** - 将中文配音合并到视频中
5. **烧录字幕** - 将中文字幕硬编码到视频中

## 技术栈

| 功能 | 技术 | 成本 |
|------|------|------|
| 视频下载 | yt-dlp | 免费 |
| 翻译 | Google Translate (上下文感知) | 免费 |
| TTS | Edge TTS / ChatTTS | 免费 |
| 视频处理 | ffmpeg | 免费 |
| 字幕烧录 | moviepy | 免费 |

## 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/douyin-video-tool.git
cd douyin-video-tool

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装系统依赖 (macOS)
brew install ffmpeg yt-dlp
```

## 使用方法

### 基本用法

```bash
./run.sh 'https://www.youtube.com/watch?v=xxxxx'
```

### TTS 选项

```bash
# Edge TTS (默认，快速，需联网)
./run.sh 'URL' --tts edge --voice yunxi

# ChatTTS (高质量，首次需下载1GB模型)
./run.sh 'URL' --tts chattts --seed 42
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

## 输出文件

处理完成后，文件保存在 `output/` 目录：

- `xxx_final.mp4` - 无字幕视频（中文配音）
- `xxx_with_subs.mp4` - 带字幕视频（中文配音 + 中文字幕）
- `xxx_zh.srt` - 中文字幕文件

## 目录结构

```
douyin-video-tool/
├── run.sh              # 入口脚本
├── scripts/
│   ├── process_free.py      # 主处理流程
│   ├── translate_google.py  # Google 翻译
│   ├── translate_google_v2.py # 上下文感知翻译
│   ├── tts_free.py          # Edge TTS
│   ├── tts_chattts.py       # ChatTTS
│   └── burn_subtitles.py    # 字幕烧录
├── downloads/          # 下载的原始视频
├── output/            # 处理后的视频
└── venv/              # Python 虚拟环境
```

## Claude Code Skill

本工具支持作为 Claude Code 的 Skill 使用。将 `skill/SKILL.md` 复制到 `~/.claude/skills/douyin-video/` 即可。

使用方式：
```
/douyin-video https://www.youtube.com/watch?v=xxxxx
```

## 推荐科普频道

- **Kurzgesagt** - 动画科普，画面精美
- **TED-Ed** - 教育动画
- **Veritasium** - 科学实验和解说
- **Mark Rober** - 工程和科学实验
- **3Blue1Brown** - 数学可视化

## License

MIT
