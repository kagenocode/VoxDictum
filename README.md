# 🎬 Video Altyazı Oluşturucu

OpenAI Whisper modeli kullanarak video dosyalarından otomatik SRT altyazı oluşturan bir Python uygulaması.

## ✨ Özellikler

- 🎙️ **Whisper AI** ile yüksek doğrulukta konuşma tanıma
- 🌍 **99+ dil** desteği (Türkçe dahil)
- ⚡ **faster-whisper** ile hızlı işleme (standart Whisper'dan ~4x hızlı)
- 📊 İlerleme çubuğu ile işlem takibi
- 🎯 VAD (Voice Activity Detection) ile sessiz kısımları otomatik atlama

## 📁 Proje Yapısı

```
firstAI/
├── main.py                        # CLI giriş noktası
├── requirements.txt               # Python bağımlılıkları
├── README.md
└── subtitle_generator/            # Ana paket
    ├── __init__.py                # Paket dışa aktarımları
    ├── audio.py                   # Video → Ses çıkarma (ffmpeg)
    ├── transcriber.py             # Ses → Metin (Whisper)
    └── srt_writer.py              # Metin → SRT dosyası
```

## 📋 Gereksinimler

- **Python 3.10+**
- **ffmpeg** (video'dan ses çıkarmak için)

## 🚀 Kurulum

### 1. ffmpeg Kurulumu

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

### 2. Python Bağımlılıkları

```bash
# Sanal ortam oluştur (önerilir)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Bağımlılıkları kur
pip install -r requirements.txt
```

### 3. GPU Desteği (Opsiyonel)

GPU kullanmak istiyorsanız PyTorch'u CUDA destekli kurun:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

## 📖 Kullanım

### Temel Kullanım

```bash
python main.py --input video.mp4
```

Bu komut `video.srt` dosyasını oluşturur (Türkçe, large-v3-turbo modeli).

### Tüm Seçenekler

```bash
python main.py --input video.mp4 \
               --model large-v3-turbo \
               --language tr \
               --device auto \
               --output altyazi.srt
```

| Parametre    | Kısaltma | Varsayılan      | Açıklama                                       |
|--------------|----------|-----------------|-------------------------------------------------|
| `--input`    | `-i`     | *(zorunlu)*     | Video dosyasının yolu                           |
| `--model`    | `-m`     | `large-v3-turbo`| Model boyutu                                    |
| `--language` | `-l`     | `tr`            | Ses dili kodu (tr, en, de, fr, vb.)             |
| `--device`   | `-d`     | `auto`          | Hesaplama cihazı (auto, cpu, cuda)              |
| `--output`   | `-o`     | `<video_adı>.srt` | Çıktı dosyası yolu                            |

### Model Seçenekleri

| Model            | Boyut   | VRAM   | Hız     | Doğruluk   |
|------------------|---------|--------|---------|------------|
| `tiny`           | ~75 MB  | ~1 GB  | ⚡⚡⚡⚡⚡ | ⭐⭐         |
| `base`           | ~140 MB | ~1 GB  | ⚡⚡⚡⚡  | ⭐⭐⭐       |
| `small`          | ~460 MB | ~2 GB  | ⚡⚡⚡   | ⭐⭐⭐⭐     |
| `medium`         | ~1.5 GB | ~4 GB  | ⚡⚡    | ⭐⭐⭐⭐⭐   |
| `large-v3`       | ~3 GB   | ~6 GB  | ⚡     | ⭐⭐⭐⭐⭐   |
| `large-v3-turbo` | ~3 GB   | ~6 GB  | ⚡⚡    | ⭐⭐⭐⭐⭐   |

> 💡 **Öneri:** GPU yoksa `small` veya `medium` modelini kullanın. GPU varsa `large-v3-turbo` en iyi seçenektir.

## 📄 Çıktı Formatı (SRT)

```srt
1
00:00:01,500 --> 00:00:04,200
Merhaba, bugün sizlerle güzel bir konu paylaşacağım.

2
00:00:04,800 --> 00:00:08,100
Bu video Python ile yapay zeka hakkında.
```

## 🔧 Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| `ffmpeg not found` | `brew install ffmpeg` ile kurun |
| Bellek yetersiz | Daha küçük model deneyin: `--model small` |
| GPU kullanılmıyor | PyTorch CUDA sürümünü kurun |
| Yanlış dil | `--language` parametresini kontrol edin |
