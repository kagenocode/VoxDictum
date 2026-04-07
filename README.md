# 🏛️ VoxDictum

> *Vox (voice) + Dictum (spoken word)* — The power that turns voice into text.

A Python application that automatically generates SRT subtitles from video files using the OpenAI Whisper model.

## ✨ Features

- 🎙️ High-accuracy speech recognition with **Whisper AI**
- 🌍 **99+ language** support (including Turkish)
- ⚡ Fast processing with **faster-whisper** (~4x faster than standard Whisper)
- 📊 Progress tracking with progress bar
- 🎯 Automatically skip silent parts with VAD (Voice Activity Detection)
- 🖥️ **Desktop GUI** — Download videos from YouTube URLs and generate subtitles
- ⬇️ YouTube video downloading with **yt-dlp**

## 📁 Project Structure

```
VoxDictum/
├── main.py                        # CLI entry point
├── gui_main.py                    # GUI entry point
├── requirements.txt               # Python dependencies
├── README.md
├── sub_gen/                       # Subtitle generation package
│   ├── __init__.py
│   ├── audio.py                   # Video → Audio extraction (ffmpeg)
│   ├── transcriber.py             # Audio → Text (Whisper)
│   └── srt_writer.py              # Text → SRT file
└── gui/                           # Desktop interface package
    ├── __init__.py
    ├── app.py                     # Main window (PyQt5)
    └── workers.py                 # Background workers (QThread)
```

## 📋 Requirements

- **Python 3.9+**
- **ffmpeg** (for extracting audio from video)

## 🚀 Installation

### 1. ffmpeg Installation

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

### 2. Python Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. GPU Support (Optional)

If you want to use GPU, install PyTorch with CUDA support:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

## 📖 Usage

### 🖥️ Desktop Application (GUI)

```bash
python gui_main.py
```

1. Paste the YouTube URL into the text field
2. Select the model and language
3. Click the **"⬇️ Download Video"** button
4. Once the download is complete, click the **"📝 Generate Subtitles"** button
5. The SRT file will be saved next to the downloaded video

### ⌨️ Command Line (CLI)

#### Basic Usage

```bash
python main.py --input video.mp4
```

This command generates a `video.srt` file (Turkish, large-v3-turbo model).

### All Options

```bash
python main.py --input video.mp4 \
               --model large-v3-turbo \
               --language tr \
               --device auto \
               --output subtitle.srt
```

| Parameter    | Shorthand | Default         | Description                                    |
|--------------|-----------|-----------------|------------------------------------------------|
| `--input`    | `-i`      | *(required)*    | Path to the video file                         |
| `--model`    | `-m`      | `large-v3-turbo`| Model size                                     |
| `--language` | `-l`      | `tr`            | Audio language code (tr, en, de, fr, etc.)     |
| `--device`   | `-d`      | `auto`          | Compute device (auto, cpu, cuda)               |
| `--output`   | `-o`      | `<video_name>.srt` | Output file path                            |

### Model Options

| Model            | Size    | VRAM   | Speed   | Accuracy   |
|------------------|---------|--------|---------|------------|
| `tiny`           | ~75 MB  | ~1 GB  | ⚡⚡⚡⚡⚡ | ⭐⭐         |
| `base`           | ~140 MB | ~1 GB  | ⚡⚡⚡⚡  | ⭐⭐⭐       |
| `small`          | ~460 MB | ~2 GB  | ⚡⚡⚡   | ⭐⭐⭐⭐     |
| `medium`         | ~1.5 GB | ~4 GB  | ⚡⚡    | ⭐⭐⭐⭐⭐   |
| `large-v3`       | ~3 GB   | ~6 GB  | ⚡     | ⭐⭐⭐⭐⭐   |
| `large-v3-turbo` | ~3 GB   | ~6 GB  | ⚡⚡    | ⭐⭐⭐⭐⭐   |

> 💡 **Tip:** If you don't have a GPU, use the `small` or `medium` model. If you have a GPU, `large-v3-turbo` is the best option.

## 📄 Output Format (SRT)

```srt
1
00:00:01,500 --> 00:00:04,200
Hello, today I'm going to share a great topic with you.

2
00:00:04,800 --> 00:00:08,100
This video is about artificial intelligence with Python.
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ffmpeg not found` | Install with `brew install ffmpeg` |
| Out of memory | Try a smaller model: `--model small` |
| GPU not being used | Install the PyTorch CUDA version |
| Wrong language | Check the `--language` parameter |
