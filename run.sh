#!/bin/bash
# 抖音科普视频一键处理工具 (完全免费版)
# 用法: ./run.sh <YouTube视频URL> [选项]
#
# 使用 Google Translate (翻译) + Edge TTS/ChatTTS (配音)
# 无需任何 API key！

set -e

PROJECT_DIR="$HOME/douyin-video-tool"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

if [ -z "$1" ]; then
    echo "抖音科普视频一键处理工具 (完全免费版)"
    echo ""
    echo "技术栈: Google Translate (翻译) + Edge TTS / ChatTTS (配音)"
    echo "无需任何 API key！"
    echo ""
    echo "用法: ./run.sh <YouTube视频URL> [选项]"
    echo ""
    echo "TTS 选项:"
    echo "  --tts edge      Edge TTS (默认，快速，需联网)"
    echo "  --tts chattts   ChatTTS (高质量，首次需下载1GB模型)"
    echo ""
    echo "Edge TTS 声音:"
    echo "  --voice yunxi     男声，年轻 (默认)"
    echo "  --voice yunyang   男声，新闻播音风格"
    echo "  --voice yunjian   男声，沉稳"
    echo "  --voice xiaoxiao  女声，温柔"
    echo "  --voice xiaoyi    女声，活泼"
    echo ""
    echo "ChatTTS 选项:"
    echo "  --seed <number>   说话人种子，不同数字产生不同声音 (默认: 42)"
    echo ""
    echo "其他选项:"
    echo "  --skip-download   跳过下载步骤（使用已下载的文件）"
    echo "  --browser <name>  浏览器 (chrome/safari/firefox/edge，默认: chrome)"
    echo ""
    echo "示例:"
    echo "  ./run.sh 'https://www.youtube.com/watch?v=xxxxx'"
    echo "  ./run.sh 'https://www.youtube.com/watch?v=xxxxx' --voice yunyang"
    echo "  ./run.sh 'https://www.youtube.com/watch?v=xxxxx' --tts chattts --seed 100"
    echo ""
    echo "高级版本 (需要 DeepL API key，翻译质量更高):"
    echo "  export DEEPL_API_KEY='your-key'"
    echo "  $VENV_PYTHON $PROJECT_DIR/scripts/process.py <URL>"
    exit 0
fi

# 执行免费版主程序
"$VENV_PYTHON" "$PROJECT_DIR/scripts/process_free.py" "$@"
